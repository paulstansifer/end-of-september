#HTTP Service s have 'url' classmethods, but since we want to create
#JS services parametrically, it's easier just to make them functions.

#TODO: we probably want to factor these into calls to <script>
#functions which we'll make return false in order to stay on-page.

def hide(idc):
  return lambda doc: "$('#%s%d').slideUp(50)" % (idc, doc.get_dc('ctxid'))

def show(idc):
  return lambda doc: "$('#%s%d').slideDown(50)" % (idc, doc.get_dc('ctxid'))

