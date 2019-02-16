

function start(){
  Graphics.initialize();
  processJSON("json/ans_easy.json", function(re){window.ans_easy = JSON.parse(re)})
  window.currentHexNumber = 10;
}

window.addEventListener("load", start, false);

window.startScene = function(){
  let scene = new Scene_Base();
  window.scene = scene;
  Graphics.render(scene);
  background = Graphics.addSprite(Graphics.Images.gameBack);
  background.render();
  window.background = background;
  createTiles();
  createSolveIcon();
  createNumberLayer();
}

function changeColor(pos){
  if(window.tilesLight[pos].visible){
    window.tilesDark[pos].show();
    window.tilesLight[pos].hide();
  }
  else{
    window.tilesDark[pos].hide();
    window.tilesLight[pos].show();
  }
}

function attachTileListener(tile, pos){
  tile.on('tap', ()=>{changeColor(pos)});
  tile.on('click', ()=>{changeColor(pos)});
}

function createTiles(){
  var tiles_dark = [], tiles_light = [];
  var size_scale = [0.2, 0.2]
  var offset     = [211*size_scale[0], 366*size_scale[1]]
  let sample = Graphics.addSprite(Graphics.Images.tileDark).hide();
  sample.scale.set(size_scale[0], size_scale[1]);

  var pos_base = [
    Graphics.appCenterWidth(sample.width) + Graphics.padding, 
    Graphics.appCenterHeight(sample.height) + Graphics.padding
  ];

  var tile_pos = [
    [pos_base[0] - offset[0] - sample.width, pos_base[1] - offset[1]],
    [pos_base[0] - offset[0], pos_base[1] - offset[1]], 
    [pos_base[0] + offset[0], pos_base[1] - offset[1]],

    [pos_base[0] - sample.width*2, pos_base[1]],
    [pos_base[0] - sample.width, pos_base[1]], 
    [pos_base[0], pos_base[1]], 
    [pos_base[0] + sample.width, pos_base[1]],

    [pos_base[0] - offset[0] - sample.width, pos_base[1] + offset[1]], 
    [pos_base[0] - offset[0], pos_base[1] + offset[1]], 
    [pos_base[0] + offset[0], pos_base[1] + offset[1]],
  ];
  window.tilePOS = tile_pos;
  let len = tile_pos.length;
  for(let i=0;i<len;++i){
    let spd = Graphics.addSprite(Graphics.Images.tileDark).hide();
    let spl = Graphics.addSprite(Graphics.Images.tileLight).hide();
    spd.scale.set(size_scale[0], size_scale[1]); spd.render();
    spl.scale.set(size_scale[0], size_scale[1]); spl.render();
    spd.setPOS(tile_pos[i][0], tile_pos[i][1]).show().activate().color = 0;
    spl.setPOS(tile_pos[i][0], tile_pos[i][1]).activate().color = 1;
    attachTileListener(spd, i);
    attachTileListener(spl, i);
    tiles_dark.push(spd);
    tiles_light.push(spl);
  }

  window.tilesDark = tiles_dark;
  window.tilesLight = tiles_light;
}

function createSolveIcon(){
  window.goIcon  = Graphics.addSprite(Graphics.Images.goIcon).show();
  window.goIconH = Graphics.addSprite(Graphics.Images.goIconH).hide();
  window.goIcon.setPOS(326,543).activate().setZ(1).render(); window.goIconH.setPOS(326,543).setZ(2).render();
  window.goIcon.on('mousedown', ()=>{window.goIconH.show();})
  window.goIcon.on('mouseup', ()=>{window.goIconH.hide();})
  window.goIcon.on('mouseout', ()=>{window.goIconH.hide();})
  window.goIcon.on('click', ()=>{solvePuzzle()});
  window.goIcon.on('tap', ()=>{
    window.goIconH.show();
    setTimeout(()=>{window.goIconH.hide()}, 300);
    solvePuzzle();
  });
}

function createNumberLayer(){
  window.numberLayer = new SpriteCanvas(0, 0, Graphics.width, Graphics.height);
  window.numberLayer.setZ(0x10).show().render();
}

function solvePuzzle(){
  window.numberLayer.clear();
  let status = "";
  for(let i=0;i<window.currentHexNumber;++i){
    let stat;
    if(window.tilesLight[i].visible){stat = 1}
    else{stat = 0;}
    if(document.getElementById("inv").checked){stat ^= 1}
    status += stat;
  }
  let sol_order = window.ans_easy[status];
  let number_map = [];
  for(let i in sol_order){
    i = parseInt(i);
    number_map[sol_order[i]] = number_map[sol_order[i]] || [];
    number_map[sol_order[i]].push(i+1);
  }
  console.log(sol_order);
  for(let i=0;i<number_map.length;++i){
    if(!number_map[i]){continue;}
    let dx = window.tilePOS[i][0], dy = window.tilePOS[i][1];
    let txt = window.numberLayer.drawText(dx, dy, number_map[i]);
    let offset = [window.tilesDark[0].width, window.tilesDark[0].height]
    txt.setPOS(dx + (offset[0]-txt.width)/2, dy + (offset[1]-txt.height)/2);
  }
}

function resetAll(){
  window.numberLayer.clear();
  for(let i=0;i<window.currentHexNumber;++i){
    window.tilesDark[i].show();
    window.tilesLight[i].hide();
  }
}