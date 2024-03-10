from functools import partial

from aiohttp import web

from main import read_file, main


async def handle(charged_words, request, max_urls=10):
    urls = request.query.get('urls')
    if urls is None:
        return web.Response(status=404, text='Not found')

    urls_list = urls.split(',')
    if len(urls_list) > max_urls:
        error_message = {'error': f'too many urls in request, should be {max_urls} or less'}
        return web.json_response(error_message, status=400)

    result_articles = await main(urls_list, charged_words)
    response_data = [{'status': status, 'url': url, 'score': rating, 'words_count': word_count}
                     for url, status, rating, word_count, _ in result_articles]
    return web.json_response(response_data)


if __name__ == '__main__':
    negative_words_path = 'charged_dict/negative_words.txt'
    positive_words_path = 'charged_dict/positive_words.txt'

    negative_words = read_file(negative_words_path)
    positive_words = read_file(positive_words_path)

    app = web.Application()
    app.add_routes([web.get('/', partial(handle, negative_words))])
    web.run_app(app)
