// seccion de login para aparicion de aviso 
const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

registerBtn.addEventListener('click', () =>{
    container.classList.add('active');
});

loginBtn.addEventListener('click', () =>
{
    container.classList.remove('active');
});


document.addEventListener("DOMContentLoaded", function() {
    const btnAceptarPrivacidad = document.getElementById('btn-aceptar-privacidad');
    const avisoPrivacidad = document.getElementById('aviso-privacidad');
    const fondoAviso = document.getElementById('fondo-aviso');

    avisoPrivacidad.classList.add('activo');
    fondoAviso.classList.add('activo');

    btnAceptarPrivacidad.addEventListener('click', () => {
        avisoPrivacidad.classList.remove('activo');
        fondoAviso.classList.remove('activo');

        localStorage.setItem('terminos-aceptados', true);
    });
});

