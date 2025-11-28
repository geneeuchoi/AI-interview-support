function saveAndRedirect() {
    const userName = document.getElementById('userName').value;
    const agenda = document.getElementById('agenda').value;

    localStorage.setItem('userName', userName);
    localStorage.setItem('agenda', agenda);

    window.location.href = '/prototype';
}
