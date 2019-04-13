objects = document.getElementsByClassName('theme');
let selected = 0;
let defaultleft = new Array();
let defaulttop = new Array();
let moved = new Array();

for (let i = 0; i < objects.length; ++i){
    moved[i] = false;
    objects[i].addEventListener('click', function()
    {
        if(!moved[i]){
            defaultleft[i] = objects[i].getBoundingClientRect().left;
            defaulttop[i] = objects[i].getBoundingClientRect().top;
            anime({
                targets: '#'+objects[i].id,
                duration: 500,
                easing: 'linear',
                left: selected * 150 + 50,
                top: 50
            })
        }
        selected++;
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
            left: defaultleft[i],
            top: defaulttop[i]-15
        })
        moved[i] = false;
    }
    selected = 0;
})
