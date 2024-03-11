from functools import partial

import pytest
from aiohttp import web

from process import read_file, process_article_main, ProcessingStatus, get_charged_words


async def handle(charged_words, request, max_urls=10):
    urls = request.query.get('urls')
    if urls is None:
        return web.Response(status=404, text='Not found')

    urls_list = urls.split(',')
    if len(urls_list) > max_urls:
        error_message = {'error': f'too many urls in request, should be {max_urls} or less'}
        return web.json_response(error_message, status=400)

    result_articles = await process_article_main(urls_list, charged_words)
    response_data = [{'status': status, 'url': url, 'score': rating, 'words_count': word_count}
                     for url, status, rating, word_count, _ in result_articles]
    return web.json_response(response_data)


@pytest.fixture
def dummy_charged_words():
    negative_test_words_path = 'charged_dict/negative_words.txt'
    positive_test_words_path = 'charged_dict/positive_words.txt'
    charged_words = get_charged_words(negative_test_words_path, positive_test_words_path)
    return charged_words


@pytest.mark.asyncio
async def test_process_article_main_successful(dummy_charged_words):
    test_articles = ['https://inosmi.ru/20240214/241584580.html']
    result_articles = await process_article_main(test_articles, dummy_charged_words)
    assert len(result_articles) == 1
    assert result_articles[0][0] == test_articles[0]
    assert result_articles[0][1] == ProcessingStatus.OK.value


@pytest.mark.asyncio
async def test_process_article_main_fetch_error(dummy_charged_words):
    test_articles = ['https://inosmi.ru/not/exist.html']
    result_articles = await process_article_main(test_articles, dummy_charged_words)
    assert len(result_articles) == 1
    assert result_articles[0][0] == test_articles[0]
    assert result_articles[0][1] == ProcessingStatus.FETCH_ERROR.value


@pytest.mark.asyncio
async def test_process_article_main_parsing_error(dummy_charged_words):
    test_articles = ['https://example.com']
    result_articles = await process_article_main(test_articles, dummy_charged_words)
    assert len(result_articles) == 1
    assert result_articles[0][0] == test_articles[0]
    assert result_articles[0][1] == ProcessingStatus.PARSING_ERROR.value


if __name__ == '__main__':
    negative_words_path = 'charged_dict/negative_words.txt'
    positive_words_path = 'charged_dict/positive_words.txt'

    negative_words = read_file(negative_words_path)
    positive_words = read_file(positive_words_path)

    app = web.Application()
    app.add_routes([web.get('/', partial(handle, negative_words))])
    web.run_app(app)
