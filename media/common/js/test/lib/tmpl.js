module('micro-templating')

test("list template", function(){
    template = [
        "<ul>",
            "<% for (var i=0; i < users.length; i++) { %>",
                "<li><%= users[i].name %></li>",
            "<% } %>",
        "</ul>"
    ];
    template = template.join("");
    list_users = tmpl(template);
    data = {users: [{name:'me'}, {name: 'myself'}]}
    equals(list_users(data), "<ul><li>me</li><li>myself</li></ul>");
});