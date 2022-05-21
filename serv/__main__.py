
import json, os

def __dir__(request_, response_, route_args_):
	folder = route_args_['dir']
	try:
		content = os.listdir('web/'+folder)
		content = '\n'.join(content)
		return response_.write_response_OK_(content_type_='text/plain', content_=content, charset_='UTF-8')
	except Exception as ex:
		return response_.write_response_not_found_()

def home(request_, response_, route_args_):
	content = '<script>location.href="web/index.html"</script>'
	return response_.write_response_OK_(content_type_='text/html', content_=content, charset_='UTF-8')

rpc_registry = {}
def ajax_(request_, response_, route_args_):
	global rpc_registry
	params_ = request_.params_
	assert 'data' in params_, '服务请求参数中缺少 data'
	data = json.loads(params_['data'])
	assert 'func_name' in data
	assert 'argv' in data
	func_name = data['func_name']
	argv = data['argv']
	assert func_name in rpc_registry, f'服务中没有登记函数 {func_name}, 所有函数: {", ".join(rpc_registry.keys())}'
	res = rpc_registry[func_name](*argv)
	json_ = json.dumps(res)
	return response_.write_response_JSON_OK_(json_)

def start_server_(port_, max_threads_):
	from .lib.http_ import Http_
	http_ = Http_(ip_='127.0.0.1', port_=port_, web_path_='web', max_threads_=max_threads_)
	http_.add_route_('/ajax', ajax_, 'GET')
	http_.add_route_('/ajax', ajax_, 'POST')
	http_.add_route_('/__dir__/{dir}', __dir__, 'GET')
	http_.add_route_('/__dir__/{dir}', __dir__, 'POST')
	http_.add_route_('/', home, 'GET')
	http_.start_()


def rpc_auto_move(board_key):
	from web.py_lib import auto_chess
	board = auto_chess._board_from_key(board_key)
	from web.py_lib import auto_chess2
	return auto_chess2.auto_move(board)

# 登记函数 RPC auto_move
rpc_registry['rpc_auto_move'] = rpc_auto_move

start_server_(8000, 100)
