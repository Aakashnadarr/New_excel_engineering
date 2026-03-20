function clearAll() {
    document.querySelectorAll('input[type=text]').forEach(i => i.value = '');
    document.querySelectorAll('.ce-particulars').forEach(d => d.textContent = '');
}