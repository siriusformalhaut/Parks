/*
// get objects whose classes are 'ltheme'
lobjects = document.getElementsByClassName('ltheme');
// for each object (note that 'forEach' is not applicable!)
for (let i = 0; i < lobjects.length; ++i){
    // onclick animation
    lobjects[i].addEventListener('click',function()
    {
        anime({
            targets: '#'+lobjects[i].id,
            translateY: 250,
            duration: 3000,
            easing: 'linear'
        });
    });    
}

objects = document.getElementsByClassName('theme');
objlen = objects.length;
for (let i = 0; i < objlen; ++i){

    anime({
        targets: '#'+objects[i].id,
        translateX: document.getElementById('explorefield').offsetWidth-objects[i].offsetWidth,
        duration: 6000,
        easing: 'linear',
        autoplay: true,
        loop: true,
        delay: 1000*i/objlen 
    })

}
*/
