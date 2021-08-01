let bubbleBtn = document.querySelectorAll(".bubble-btn");

function animateButton(e) {
    e.target.classList.add('animate');
    setTimeout(function () {
        e.target.classList.remove('animate');
    }, 800);
    let form = document.querySelector("form");
    form.submit();
};


for (let i = 0; i < bubbleBtn.length; i++) {
    bubbleBtn[i].addEventListener('click', animateButton);
}