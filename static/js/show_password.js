function ShowPassword(obj) {
    var x = document.getElementById("myInput");
    x.type = (x.type == "password") ? "text" : "password";

    obj.classList.toggle("fa-eye-slash");
}