objects = document.getElementsByClassName('theme');
explorefield = document.getElementById('explorefield');
let leftbuffer = 0;
let defaultleft = new Array();
let defaulttop = new Array();
let moved = new Array();

for (let i = 0; i < objects.length; ++i){
    moved[i] = false;
    objects[i].addEventListener('click', function()
    {
        if(!moved[i]){
            defaultleft[i] = objects[i].getBoundingClientRect().left+window.pageXOffset;
            defaulttop[i] = objects[i].getBoundingClientRect().top+window.pageYOffset;
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
        if(moved[i]){
            anime({
                targets: '#'+objects[i].id,
                duration: 500,
                easing: 'linear',
                left: defaultleft[i]-window.pageXOffset-explorefield.getBoundingClientRect().left,
                top: defaulttop[i]-window.pageYOffset-explorefield.getBoundingClientRect().top
            })
            moved[i] = false;
        }
    }
    leftbuffer = 0;
})
