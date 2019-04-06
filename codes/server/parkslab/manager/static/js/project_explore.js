var object = document.getElementById('astronomy');
object.addEventListener('click',function()
{
    anime({
        targets: '#astronomy',
        translateX: 250,
        duration: 3000,
        easing: 'linear'
    });
});
