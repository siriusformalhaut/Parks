objects = document.getElementsByClassName('theme');
let leftbuffer = 0;
let defaultleft = new Array();
let defaulttop = new Array();
let moved = new Array();

for (let i = 0; i < objects.length; ++i){
    moved[i] = false;
    objects[i].addEventListener('click', function()
    {
        if(!moved[i]){
            defaultleft[i] = objects[i].getBoundingClientRect().left+window.scrollX*0.775;
            defaulttop[i] = objects[i].getBoundingClientRect().top+window.scrollY*0.775;
            anime({
                targets: '#'+objects[i].id,
                duration: 500,
                easing: 'linear',
                left: leftbuffer + 50,
                top: 50
            })
        }
        leftbuffer += objects[i].getBoundingClientRect().width;
        moved[i] = true;
    })
}

ObjReset = document.getElementsByClassName('reset');
ObjReset[0].addEventListener('click', function()
{   
    for (let i = 0; i < objects.length; ++i){
        anime({
            targets: '#'+objects[i].id,
            duration: 500,
            easing: 'linear',
            left: defaultleft[i]-window.scrollX,
            top: defaulttop[i]-window.scrollY
        })
        moved[i] = false;
    }
    leftbuffer = 0;
})
