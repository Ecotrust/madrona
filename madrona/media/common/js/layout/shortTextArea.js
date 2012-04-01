
function limit_to(textarea, max_chars, chars_used_el, alert_truncate) {
    if (textarea.value.length > max_chars) {
        if(alert_truncate) {
            alert("The current text value exceeds the character limit; Any text after " + max_chars + " characters will be truncated");
        }
        textarea.value = textarea.value.substring(0, max_chars);
        textarea.focus();
    }
    document.getElementById(chars_used_el).innerHTML = textarea.value.length;
}
