var flag = true;                              //判断是否要提交form
function checkUsername(){
    var Reg = /^(\w)*$/
    var x = document.getElementById('username')
    var y = document.getElementById('stgcheck');
    y.style.color = '#f00'
    y.style.fontSize = '0.8em'
    if (Reg.test(x.value) && x.value.length > 3){
        y.innerHTML = ''
    }
    else if (x.value.length < 4){
        y.innerHTML = '用户名太短';
        flag = false;
        //console.log(flag)
    }
    else{
        y.innerHTML = '请用字母或数字来组成用户名！';
        flag = false;
        //console.log(flag)
    }
}

var z = document.getElementById('spanpsw')

function checkPassword(){
    var password1 = document.getElementById('password1')
    var password2 = document.getElementById('password2')
    if (password1.value != password2.value){
        z.innerHTML = '两次输入密码不一样！'
    }
    else if (password2.value.length == 0){
        z.innerHTML = ''
    }
    else{
        z.innerHTML = '&radic;'
    }
}

function checkSubmit(){
    if (flag == false){
        return false;
    }
    else{
        return true;
    }
}