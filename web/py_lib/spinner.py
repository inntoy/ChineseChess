

def html(tag, attrs=None, style=None):
	elt = javascript.document.createElement(tag)
	if attrs is not None:
		for k,v in attrs.items():
			elt.setAttribute(k,v)
	if style is not None:
		style = ';'.join([f'{k}:{v}' for k,v in style.items()])
		elt.setAttribute('style',style)
	return elt

_elt = None

def _get_elt():
	global _elt
	if _elt is None:
		elt = html('div', {'class':'modal spinner-modal', 'data-backdrop':'static',
			'tabindex':'-1', 'role':'dialog', 'aria-labelledby':'spinnerModalLabel', 
			'aria-hidden':'true'})
		javascript.document.body.appendChild(elt)
		center = html('div', {'class':'d-flex justify-content-center modal-dialog-centered'})
		elt.appendChild(center)
		spinner = html('div', {'class':'spinner-border text-light', 'role':'status', 'style':'width: 1rem; height: 1rem;'})
		center.appendChild(spinner)
		_elt = javascript.jQuery(elt)
	return _elt

def show():
	_get_elt().modal('show')

def hide():
	_get_elt().fadeOut()
	_get_elt().modal('hide')

