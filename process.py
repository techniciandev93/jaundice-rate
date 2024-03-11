import asyncio
import logging
import time
from contextlib import contextmanager
from enum import Enum

import aiohttp

import anyio
import pymorphy2
from async_timeout import timeout

import adapters
from adapters.inosmi_ru import sanitize
from text_tools import split_by_words, calculate_jaundice_rate


logger = logging.getLogger('jaundice-rate')


@contextmanager
def measure_time():
    start = time.perf_counter()
    yield lambda: time.perf_counter() - start


class ProcessingStatus(Enum):
    OK = 'OK'
    FETCH_ERROR = 'FETCH_ERROR'
    PARSING_ERROR = 'PARSING_ERROR'
    TIMEOUT = 'TIMEOUT'


async def process_article(session, morph, charged_words, url, result_articles, wait_timeout=10):
    try:
        async with timeout(wait_timeout):
            async with session.get(url) as response:
                with measure_time() as analysis_time:
                    response.raise_for_status()
                    html = await response.text()
                    sanitize_result = sanitize(html, plaintext=True)
                    words = await split_by_words(morph, sanitize_result)
                    score = calculate_jaundice_rate(words, charged_words)

                result_articles.append((url, ProcessingStatus.OK.value, score, len(words), analysis_time()))
    except aiohttp.ClientError:
        result_articles.append((url, ProcessingStatus.FETCH_ERROR.value, None, None, 0))
    except adapters.ArticleNotFound:
        result_articles.append((url, ProcessingStatus.PARSING_ERROR.value, None, None, 0))
    except asyncio.TimeoutError:
        result_articles.append((url, ProcessingStatus.TIMEOUT.value, None, None, 0))


async def process_article_main(urls, charged_words):
    result_articles = []
    morph = pymorphy2.MorphAnalyzer()
    async with aiohttp.ClientSession() as session:
        async with anyio.create_task_group() as tg:
            for url in urls:
                tg.start_soon(process_article, session, morph, charged_words, url, result_articles)

    for url, status, rating, word_count, analysis_time in result_articles:
        logging.info(f'URL: {url}\nСтатус: {status}\nРейтинг: {rating}\nСлов в статье {word_count}')
        logging.info(f'Анализ закончен за {analysis_time:.2f} сек')
    return result_articles


def read_file(file_path):
    with open(file_path, 'r', encoding="utf8") as file:
        return file.read().split('\n')


def get_charged_words(negative_words_path, positive_words_path):
    charged_words = []
    negative_words = read_file(negative_words_path)
    positive_words = read_file(positive_words_path)
    charged_words.extend(negative_words)
    charged_words.extend(positive_words)
    return charged_words


if __name__ == '__main__':
    negative_words_path = 'charged_dict/negative_words.txt'
    positive_words_path = 'charged_dict/positive_words.txt'

    words = get_charged_words(negative_words_path, positive_words_path)

    test_articles = ['https://inosmi.ru/20240214/241584580.html',
                     'https://inosmi.ru/economic/20190629/245384784.html',
                     'https://inosmi.ru/20240305/litva-268120074.html',
                     'https://inosmi.ru/20240305/voyska-268117040.html',
                     'https://inosmi.ru/20240305/sholts-268116706.html',
                     'https://inosmi.ru/not/exist.html',
                     'https://lenta.ru/brief/2021/08/26/afg_terror/'
                     ]

    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
    )
    logger.setLevel(logging.INFO)

    anyio.run(process_article_main, test_articles, words)
