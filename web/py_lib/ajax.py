
def send(data, callback):
	ajax = javascript.XMLHttpRequest.new()
	done = False
	def onerror(e):
		nonlocal done
		statusText = ajax.statusText.data()
		if statusText=='':
			statusText = '未能从服务器获取信息'
		if not done:
			done = True
			callback({'error': statusText})
	def onreadystatechange(e):
		nonlocal done
		if (ajax.readyState.data() == 4): # XMLHttpRequest.DONE
			status = ajax.status.data()
			if ((status>=200) and (status<300)) or (status==304):
				if not done:
					done = True
					callback(ajax.response.data())
			else:
				onerror(None)
	ajax.onreadystatechange = onreadystatechange
	ajax.onerror = onerror
	ajax.open('POST', '/ajax', True)
	ajax.setRequestHeader("Content-type", "application/x-www-form-urlencoded")
	ajax.responseType = 'json'
	post_data = {'data':javascript.JSON.stringify(data)}
	ajax.send(javascript.URLSearchParams.new(post_data))

class _RPC_service:
	def __init__(self):
		pass
	def __getattr__(self, func_name):
		return _RPC_func(func_name)
		
class _RPC_func:
	def __init__(self, func_name):
		self.func_name = func_name
	def __call__(self, *argv):
		import time
		done = False
		res = None
		error = None
		def callback(data):
			nonlocal res
			nonlocal done
			nonlocal error
			if isinstance(data, dict) and ('error' in data):
				error = data['error']
				done = True
				return
			res = data
			done = True
		data = {'func_name':self.func_name, 'argv':argv}
		send(data, callback)
		while not done:
			time.sleep(.1)
		if error is not None:
			raise RuntimeError(error) 
		return res

rpc = _RPC_service()
