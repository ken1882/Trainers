if (document.querySelector('input[value="0"]') != undefined) {
    let angle = parseInt(swf.attributes.swf.match(/Kreludor=(\d+)/)[1]);
    let lnt = [11, 33, 56, 78, 101, 123, 146, 168, 191, 213, 236, 258, 281, 303, 326, 348, 360];
    let idx = lnt.findIndex((i) => { return angle <= i; });
    idx = idx == 16 ? 8 : idx < 8 ? idx + 8 : idx - 8;

    let ans = document.querySelector(`.content input[value="${idx}"]`);
    ans.parentNode.style.background = "#000";
    ans.parentNode.id = "answer";
}