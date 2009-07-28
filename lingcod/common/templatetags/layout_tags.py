from django import template
from django.template import resolve_variable
register = template.Library()

@register.tag(name="home_link")
def do_home_link(parser, token):
    """Provides a back button link to the home panel.
    """
    tokens = token.split_contents()
    print tokens
    if len(tokens) == 1:
        href = "#"
        text = "Back Home"
    elif len(tokens) == 2:
        href = "#"
        text = tokens[1]
    elif len(tokens) == 3:
        text = tokens[1]
        href = '#' + tokens[2].replace(' ', '')
    else:
        raise template.TemplateSyntaxError, "%r tag accepts no more than 2 arguments." % token.contents.split()[0]
    return HomeLinkNode(href, text)

class HomeLinkNode(template.Node):
    def __init__(self, href, text):
        self.href = href
        self.text = text
    
    def render(self, context):
        return """
            <a class="back_link" href="%s">%s</a>
        """ % (self.href, self.text)
        
@register.tag(name="back_link")
def do_back_link(parser, token):
    """Provides a back button linking to the given url, displaying the specified title.
    """
    tokens = token.split_contents()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError, "%r tag requires at least 2 arguments, a title, url and optionally a quoted tab target." % token.contents.split()[0]
    
    title = tokens[1]
    urlvar = tokens[2]
    
    if not (title[0] == title[-1] and title[0] in ('"', "'")):
        raise template.TemplateSyntaxError, "%r tag requires at least 2 arguments, a title, url and optionally a quoted tab target." % token.contents.split()[0]
    
    if len(tokens) == 4:
        tabid = tokens[3]
        if not (tabid[0] == tabid[-1] and tabid[0] in ('"', "'")):
            raise template.TemplateSyntaxError, "Tab name must be in quotes."
        tab_id = tab_id.replace('"', '').replace("'", "")
        return BackLinkNode(title, urlvar, tab=tab_id)
    else:
        return BackLinkNode(title[1:-1], urlvar)

class BackLinkNode(template.Node):
    def __init__(self, title, urlvar, tab=None):
        self.title = title
        self.urlvar = urlvar
        self.tab = tab
    
    def render(self, context):
        url = resolve_variable(self.urlvar, context)
        if self.tab != None:
            url = url + '#' + self.tab
        return """
            <a class="back_link" href="%s">%s</a>
        """ % (url, self.title)
        

@register.tag(name="footer")
def do_footer(parser, token):
    """Use to create a footer area at the bottom of the panel.
    """
    nodelist = parser.parse(('endfooter',))
    parser.delete_first_token()
    return FooterNode(nodelist)

class FooterNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist
    def render(self, context):
        print self.nodelist
        output = self.nodelist.render(context)
        return '<div class="sidebar-footer">%s</div>' % (output,)
        
        
@register.tag(name="panel")
def do_panel(parser, token):
    """Creates markup for a panel displayed using the panelManager widget.
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument. You must give your panel a title." % token.contents.split()[0]

    nodelist = parser.parse(('endpanel',))
    parser.delete_first_token()
    return PanelNode(nodelist, title)

class PanelNode(template.Node):
    def __init__(self, nodelist, title):
        self.nodelist = nodelist
        self.title = title

    def render(self, context):
        if not (self.title[0] == self.title[-1] and self.title[0] in ('"', "'")):
            self.title = resolve_variable(self.title, context)
        else:
            self.title = self.title[1:-1]        
        output = self.nodelist.render(context)
        return """<div class="sidebar-panel">
            <div class="sidebar-header">
                <h1>%s</h1>
            </div>
            <div class="sidebar-body">
                <div class="sidebar-wrapper">
                    %s
                </div>
            </div>
        </div>
        """ % (self.title, output)
        
@register.tag(name="printable")
def do_printable(parser, token):
    """Use this tag to specify that the current panel should be accessible via
    its url as a printable/static page in addition to the dynamic sidebar 
    form.
    """
    return PrintableNode()

class PrintableNode(template.Node):

    def render(self, context):
        return """
            <a class="printable" href="#" target="_blank">Print View</a>
        """

@register.tag(name="tabpanel")
def do_tabpanel(parser, token):
    """Creates markup for a panel that contains many tabs using the tab tag.
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument. You must give your tabpanel a title." % token.contents.split()[0]
    nodelist = parser.parse(('endtabpanel',))
    parser.delete_first_token()
    return TabPanelNode(nodelist, title)

class TabPanelNode(template.Node):
    def __init__(self, nodelist, title):
        self.nodelist = nodelist
        self.title = title

    def render(self, context):
        # print self.nodelist
        if not (self.title[0] == self.title[-1] and self.title[0] in ('"', "'")):
            self.title = resolve_variable(self.title, context)
        else:
            self.title = self.title[1:-1]
        output = self.nodelist.render(context)
        list_items = ''
        for node in self.nodelist:
            if node.__class__.__name__ is 'TabNode':
                list_items += """
                    <li><a href="#%s">%s</a></li>
                """ % (node.tab_id, node.title)
        return """<div class="sidebar-panel">
            <div class="sidebar-header">
                <h1>%s</h1>
            </div>
            <ul class="tabs">
                %s
            </ul>
            <div class="sidebar-body">
                <div class="sidebar-wrapper">
                    %s
                </div>
            </div>
        </div>
        """ % (self.title, list_items, output)
                
@register.tag(name="tab")
def do_tab(parser, token):
    """Create a tab within a tab_panel.
    """
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, title = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError, "%r tag requires a single argument. You must give your tab a title." % token.contents.split()[0]

    nodelist = parser.parse(('endtab',))
    parser.delete_first_token()
    return TabNode(nodelist, title)

class TabNode(template.Node):
    def __init__(self, nodelist, title):
        self.nodelist = nodelist
        self.title = title
        self.tab_id = title.replace("'", "").replace('"', '').replace(' ', '')
    def render(self, context):
        if not (self.title[0] == self.title[-1] and self.title[0] in ('"', "'")):
            self.title = resolve_variable(self.title, context)
        else:
            self.title = self.title[1:-1]

        output = self.nodelist.render(context)
        return """<div id="%s" class="sidebar-body">
            <div class="sidebar-wrapper">
                %s
            </div>
        </div>
        """ % (self.tab_id, output)
