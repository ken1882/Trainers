/**---------------------------------------------------------------------------
 * >> The root object of the display tree.
 *
 * @class Stage
 * @extends PIXI.Container
 */
class Stage extends PIXI.Container{
  /**-------------------------------------------------------------------------
   * @constructor
   * @memberof Stage
   */
  constructor(...args){
    super(...args);
    this.initialize.apply(this, arguments);
  }
  /**-------------------------------------------------------------------------
   * > Object initialization
   * @memberof Stage
   */
  initialize(){
    PIXI.Container.call(this);
    // The interactive flag causes a memory leak.
    this.interactive = false;
  }
}
/**----------------------------------------------------------------------------
 * >> The static class that carries out graphics processing.
 * @namespace Graphics
 */
class Graphics{
  constructor(){
    throw new Error('This is a static class');
  }
  /**----------------------------------------------------------------------------
   * > Module Initialization
   * @memberof Graphics
   * @property {number} _width          - width of app canvas
   * @property {number} _height         - height of app canvas
   * @property {number} _padding        - default padding of app canvas
   * @property {number} _spacing        - width of space for sprites seperate
   * @property {number} _frameCount    - frames passed after app starts
   * @property {object} _spriteMap     - Mapping sprite name to sprite instance
   * @property {boolean} _loaderReady  - whether the loader is completed
   */  
  static initialize(){
    this._width   = 700;
    this._height  = 600;
    this._padding = 32;
    this._spacing = 8;
    this._lineHeight = 24;
    this._frameCount = 0;
    this._spriteMap  = {};
    this.DefaultFontSetting = {
      fontFamily: "Arial",
      fontSize: 20,
      align: "center",
      fill: 0x00BFFF,
    }

    this.createApp();
    this.initImages();
    this.initRenderer();
    this.initLoader();
  }
  /**------------------------------------------------------------------------
   * > Define images
   */
  static initImages(){
    this.Images = {};
    this.Images.gameBack  = "assets/bg.png";
    this.Images.tileLight = "assets/tl.png";
    this.Images.tileDark  = "assets/td.png";
    this.Images.goIcon    = "assets/go.png";
    this.Images.goIconH   = "assets/go_h.png";
    this.resources = []
    for(let prop in this.Images){
      if(this.Images.hasOwnProperty(prop)){
        this.resources.push(this.Images[prop])
      }
    }
  }
  /**------------------------------------------------------------------------
   * > Getter functions
   */
  static get width(){return this._width;}
  static get height(){return this._height;}
  static get padding(){return this._padding;}
  static get spacing(){return this._spacing;}
  static get lineHeight(){return this._lineHeight;}
  /**----------------------------------------------------------------------------
   * > Create main viewport
   * @property {PIXI.Application} app - the PIXI web application
   */  
  static createApp(){
    this.app = new PIXI.Application(
      {
        width: this._width,
        height: this._height,
        antialias: true,
        backgroundColor: this.AppBackColor,
      }
    );
    this.app.x = this.screenCenterWidth();
    this.app.y = this.padding * 3;
    this.app.width  = this._width;
    this.app.height = this._height;
    this.app.view.id = "Game"
    this.app.view.style.left = this.app.x + 'px';
    this.app.view.style.top  = this.app.y + 'px';
    this.app.view.style.zIndex = 0;
  }
  /**-------------------------------------------------------------------------
   * > Initialize PIXI Loader
   * @property {PIXI.loaders.Loader} loader - PIXI resources loader
   */
  static initLoader(){
    this.loader = PIXI.loader;
    this.loader.onProgress.add( function(){Graphics._loaderReady = false;} );
    this.loader.onComplete.add( function(){Graphics._loaderReady = true;} );
    this.loader.add(this.resources).load(function(){
      window.startScene();
    });
  }
  /**----------------------------------------------------------------------------
   * @property {PIXI.WebGLRenderer} renderer - the rending software of the app
   */
  static initRenderer(){
    this.renderer = PIXI.autoDetectRenderer(this._width, this._height);
    this.renderer.plugins.interaction.interactionFrequency = 100
    document.app = this.app;
    document.getElementById('Game').replaceWith(this.app.view);
  }
  /**-------------------------------------------------------------------------
   * > Pre-load all image assets
   */
  static preloadAllAssets(progresshandler, load_ok_handler){
    if(!progresshandler){ progresshandler = function(){} }
    if(!load_ok_handler){ load_ok_handler = function(){} }
    this.IconsetImage = new Image();
    this.IconsetImage.src = this.Iconset;
    this.windowSkins = {}
    this.WindowSkinSrc.forEach(function(path){
      if(path){
        Graphics.windowSkins[path]     = new Image();
        Graphics.windowSkins[path].src = path;
      }
    })
    this.loader.add(this.Images);
    this.loader.onProgress.add(progresshandler);
    this.loader.onError.add(this.onLoadError.bind(this));
    this.loader.load(load_ok_handler);
    this.loader.onComplete.add(function(){
      this._assetsReady = true;
    }.bind(this));
  }
  /*------------------------------------------------------------------------*/
  static onLoadError(msg, loader, rss){
    reportError(new ResourceError("PIXI Loader error:\n" + msg + '\n' + 'filename: ' + rss.name));
    let txt = "There was an error while loading resources, probably caused by github.io server error " +
              "and should be resolved after reload the page. Would you like to reload the page?";
    requestReload(txt);
  }
  /**-------------------------------------------------------------------------
   * > Return textire of pre-loaded resources
   * @param {string} name - name of resources
   * @param {Rectangle} [srect] - (Opt)Souce Slice Rect of the texture
   */  
  static loadTexture(name, srect){
    if(srect){
      return new PIXI.Texture(PIXI.loader.resources[name].texture, srect);
    }
    return PIXI.loader.resources[name].texture;
  }
  /**-------------------------------------------------------------------------
   * > Check whether loader has loaded all resources
   * @returns {boolean}
   */  
  static isReady(){
    return this._loaderReady && this._assetsReady;
  }
  /**-------------------------------------------------------------------------
   * > Render scene(stage)
   * @param {Scene_Base} stage - the scene to be rendered
   */  
  static render(stage){
    if(stage){
      this.app.stage = stage;
      this.renderer.render(stage)
    }
  }
  /**-------------------------------------------------------------------------
   * > Render sprite to current scene
   * @param {Sprite} sprite - the sprite to be rendered
   */
  static renderSprite(sprite){
    if(window.scene.children.indexOf(sprite) > -1){return ;}
    if(sprite.isWindow){return this.renderWindow(sprite);}
    window.scene.addChild(sprite);
    window.scene.children.sort((a,b) => (a.zIndex || 0) - (b.zIndex || 0))
  }
  /**-------------------------------------------------------------------------
   * > Get center x-pos of object in screen
   * @param {number} x - the object's width
   * @returns {number} - the x-pos after centered
   */  
  static screenCenterWidth(x = this._width){
    return Math.max((screen.width - x) / 2, 0);
  }
  /**-------------------------------------------------------------------------
   * > Get center y-pos of object in screen
   * @param {number} y - the object's height
   * @returns {number} - the y-pos after centered
   */  
  static screenCenterHeight(y = this._height){
    return Math.max((screen.height - y) / 2 - this._padding * 2, 0);
  }
  /**-------------------------------------------------------------------------
   * > Get center x-pos of object in canva
   * @param {number} x - the object's width
   * @returns {number} - the x-pos after center
   */  
  static appCenterWidth(x = 0){
    return (this._width - x) / 2;
  }
  /**-------------------------------------------------------------------------
   * > Get center y-pos of canva
   * @param {number} y - the object's height
   * @returns {number} - the y-pos after center
   */  
  static appCenterHeight(y = 0){
    return (this._height - y) / 2;
  }
  /**-------------------------------------------------------------------------
   * > Frame update
   * @memberof Graphics
   */  
  static update(){
  }
  /**-------------------------------------------------------------------------
   * > Add sprite and build a instance name map
   * @param {string} image_name - the path to the image
   * @param {string} instance_name - the name give to the sprite after created
   * @returns {Sprite} - the created sprite
   */  
  static addSprite(image_name, instance_name = null){
    var sprite = new Sprite(Graphics.loadTexture(image_name));
    if(instance_name == null){instance_name = image_name;}
    sprite.name = instance_name;
    this._spriteMap[instance_name] = sprite;
    return sprite;
  }
  /**-------------------------------------------------------------------------
   * > Add text sprite and build a instance name map
   * @param {string} text - the text to show
   * @param {string} instance_name - the name give to the sprite after created
   * @param {object} fontsetting - the font setting for the text
   * @returns {PIXI.Sprite} - the created sprite
   */  
  static addText(text, instance_name = null, fontsetting = Graphics.DefaultFontSetting){
    var sprite = new PIXI.Text(text, fontsetting);
    if(instance_name == null){instance_name = text;}
    sprite.name = instance_name;
    this._spriteMap[instance_name] = sprite;
    return sprite;
  }
  /**-------------------------------------------------------------------------
   * > Remove object in current scene
   * @param {PIXI.Sprite|string} - the sprite/instance name of sprite to remove
   */
  static removeSprite(...args){
    args.forEach(function(obj){
      if(isClassOf(obj, String)){ obj = Graphics._spriteMap[obj]; }
      delete Graphics._spriteMap[obj.name];
      window.scene.removeChild(obj);
    })
  }
}

/**---------------------------------------------------------------------------
 * The extended class of PIXI.Sprite
 *
 * @class Sprite
 * @constructor
 * @extends PIXI.Sprite
 * @property {boolean} static - When is child, the position won't effected by
 *                              parent's display origin (ox/oy)
 * 
 * @property {Number} speed   - Pixel delta per average frame
 * @property {Number} realX   - The final x position the sprite should be
 * @property {Number} realY   - The final y position the sprite should be
 */
class Sprite extends PIXI.Sprite{
  /**-------------------------------------------------------------------------
   * @constructor
   * @memberof Sprite
   * @param {Texture} texture - A PIXI.Texture to convert to sprite
   */
  constructor(...args){
    super(...args);
    this.realX = this.x;
    this.realY = this.y;
    this.setZ(0);
    this.static = false;
    this.interactive = false;
    this.speed = 8;
    return this;
  }
  /*-------------------------------------------------------------------------*/
  get z(){return this.zIndex;}
  /*-------------------------------------------------------------------------*/
  get rect(){
    return new Rect(this.x, this.y, this.width, this.height);
  }
  /*-------------------------------------------------------------------------*/
  update(){
    this.updateMovement();
  }
  /*-------------------------------------------------------------------------*/
  updateMovement(){
    if(this.deltaX == 0 && this.deltaY == 0){return ;}
    if(this.realX == this.x && this.realY == this.y){
      this.deltaX = 0; this.deltaY = 0;
      this.callMoveCompleteFunction();
      return ;
    }
    if(this.x < this.realX){
      this.x = Math.min(this.realX, this.x + this.deltaX * Graphics.speedFactor);
    }
    else{
      this.x = Math.max(this.realX, this.x + this.deltaX * Graphics.speedFactor);
    }
    if(this.y < this.realY){
      this.y = Math.min(this.realY, this.y + this.deltaY * Graphics.speedFactor);
    }
    else{
      this.y = Math.max(this.realY, this.y + this.deltaY * Graphics.speedFactor);
    }
  }
  /**-------------------------------------------------------------------------
   * Move to given position step by step (called from update)
   */
  moveto(x, y, fallback=null){
    if(x == null){x = this.x;}
    if(y == null){y = this.y;}
    if(this.isMoving){this.callMoveCompleteFunction();}
    this.moveCompleteFallback = fallback;
    this.realX = x;
    this.realY = y;
    let dx = (this.realX - this.x), dy = (this.realY - this.y);
    let h = Math.sqrt(dx*dx + dy*dy);
    this.deltaX = this.speed * dx / h;
    this.deltaY = this.speed * dy / h;
    if(this.deltaX == 0 && this.deltaY == 0){
      this.callMoveCompleteFunction();
    }
  }
  /*-------------------------------------------------------------------------*/
  callMoveCompleteFunction(delay=0){
    if(!this.moveCompleteFallback){return ;}
    if(delay > 0){
      EventManager.setTimeout(()=>{
        if(this.moveCompleteFallback){
          this.moveCompleteFallback();
          this.moveCompleteFallback = null;
        };
      }, delay);
    }
    else{
      this.moveCompleteFallback();
      this.moveCompleteFallback = null;
    }
  }
  /*-------------------------------------------------------------------------*/
  resize(w, h){
    if(w === null){w = this.width;}
    if(h === null){w = this.height;}
    var scale = [w / this.width, h / this.height]
    this.setTransform(this.x, this.y, scale[0], scale[1]);
    this.children.forEach(function(sp){
      sp.setTransform(sp.x, sp.y, scale[0], scale[1]);
    });
    return this;
  }
  /*-------------------------------------------------------------------------*/
  clear(){
    for(let i=0;i<this.children.length;++i){
      if(!this.children[i].destroy){continue;}
      this.children[i].destroy({children: true});
    }
    this.children = []
    return this;
  }
  /*-------------------------------------------------------------------------*/
  setPOS(x, y){
    if(this.isMoving){this.callMoveCompleteFunction(2);}
    super.setPOS(x, y);
    this.realX = this.x;
    this.realY = this.y;
    return this;
  }
  /*-------------------------------------------------------------------------*/
  fillRect(x, y, w, h, c){
    let rect = new PIXI.Graphics();
    rect.beginFill(c);
    rect.drawRect(x, y, w, h);
    rect.endFill();
    rect.zIndex = 2;
    rect.alpha = this.opacity;
    this.addChild(rect);
    return rect;
  }
  /*-------------------------------------------------------------------------*/
  drawText(x, y, text, font = Graphics.DefaultFontSetting){
    if(!font){font = Graphics.DefaultFontSetting}
    let txt = new PIXI.Text(text, font);
    txt.alpha  = this.opacity;
    txt.setPOS(x,y).setZ(2);
    this.addChild(txt);
    return txt;
  }
  /**-------------------------------------------------------------------------
   * > Draw Icon in Iconset
   * @param {Number} icon_index - the index of the icon in Iconset
   * @param {Number} x - the draw position of X
   * @param {Number} y - the draw position of Y
   */
  drawIcon(icon_index, x, y){
    icon_index = parseInt(icon_index);
    let src_rect = clone(Graphics.IconRect);
    src_rect.x = icon_index % Graphics.IconRowCount * src_rect.width;
    src_rect.y = parseInt(icon_index / Graphics.IconRowCount) * src_rect.height;
    let sx = src_rect.x, sy = src_rect.y, sw = src_rect.width, sh = src_rect.height;
    let bitmap = new Bitmap(0, 0, sw, sh);
    bitmap.blt(Graphics.IconsetImage, sx, sy, sw, sh, 0, 0, sw, sh);
    let texture = new PIXI.Texture.fromCanvas(bitmap.canvas);
    let iconSprite = new Sprite(texture);
    iconSprite.setPOS(x, y).setZ(2);
    this.addChild(iconSprite);
    return iconSprite;
  }
  /*-------------------------------------------------------------------------*/
  addChild(...args){
    super.addChild(...args);
    this.children.sort((a,b) => (a.zIndex || 0) - (b.zIndex || 0));
  }
  /*-------------------------------------------------------------------------*/
  render(){
    Graphics.renderSprite(this);
  }
  /*-------------------------------------------------------------------------*/
  remove(){
    Graphics.removeSprite(this);
  }
  /*-------------------------------------------------------------------------*/
  getStringWidth(text, font = Graphics.DefaultFontSetting){
    return new PIXI.Text(text, font).width;
  }
  /*-------------------------------------------------------------------------*/
  textWrap(text, font = Graphics.DefaultFontSetting){
    if(!text){return ;}
    let paddingW = Graphics.padding / 2; // Padding width
    if(this.width - paddingW - Graphics.spacing < 0){
      console.error("Window too small to text warp: " + getClassName(text));
      return text;
    }

    // Line width
    let lineWidth = this.width - paddingW;

    let formated = "";  // Formated string to return
    let curW = 0;       // Current Line Width
    let line = "";      // Current line string
    let strings = text.split(/[\r\n ]+/) // Split strings
    let minusW = this.getStringWidth('-', font);
    let spaceW = this.getStringWidth(' ', font);
    let endl = false;   // End Of Line Flag
    let strW = 0;       // Current processing string width
    let flag_simple = (DataManager.language.indexOf("zh") != -1);
    let str = null; // Current processing string
    debug_log("-----Text Wrap-----");
    debug_log("Original: " + text);
    if(!flag_simple){
      while(str = strings[0]){
        if((str || '').length == 0){continue;}
        strW = this.getStringWidth(str, font);
        endl = false; 
        // String excessed line limit
        if(strW + paddingW > lineWidth){
          line = "";
          let curW = minusW, last_i = 0;
          let processed = false;
          // Process each character in current string
          for(let i=0;i<str.length;++i){
            strW = this.getStringWidth(str[i], font);
            last_i = i;
            // Display not possible
            if(!processed && curW + strW >= lineWidth){
              return text;
            } // Current character acceptable
            else if(curW + strW < lineWidth){
              curW += strW;
              line += str[i];
              processed = true;
            } // Unable to add more
            else{
              break;
            }
          }
  
          line += '-'
          strings[0] = str.substr(last_i, str.length);
          endl = true;
        } // current string can fully add to line
        else if(curW + strW < lineWidth){
          curW += strW + spaceW;
          line += strings.shift() + ' ';
          if(strings.length == 0){endl = true;}
        }
        else{
          endl = true;
        }
        debug_log("Current: " + line);
        if(endl){
          formated += line;
          if(strings.length > 0){formated += '\n';}
          line = "";
          curW = paddingW;
          debug_log("Endl merged: " + formated);
        }
      }
    } // else: just process one by one
    else{
      for(let i=0;i<text.length;++i){
        strW = this.getStringWidth(text[i], font);
        if(curW + strW >= lineWidth){
          formated += line + '\n';
          curW = strW;
          line = text[i];
        }
        else{
          line += text[i];
          curW += strW;
        }
      }
    }
    if(line.length > 0){formated += line;}
    debug_log("Final: " + formated);
    debug_log("-------------------")
    return formated;
  }
  /*-------------------------------------------------------------------------*/
  get translucentAlpha(){return 0.4;}
  /*-------------------------------------------------------------------------*/
  get isMoving(){return this.x != this.realX || this.y != this.realY;}
  /**-------------------------------------------------------------------------
   * > Getter function
   */
  get opacity(){return parseFloat(this.alpha);}
  /*-------------------------------------------------------------------------*/
}

/**---------------------------------------------------------------------------
 * > An object holds collection of sprites, does not an actual sprite 
 * class itself. Supposed to be superclass so won't call initialize itself.
 * 
 * @class
 * @extends Sprite
 * @property {Number} x - X position in app
 * @property {Number} y - Y position in app
 * @property {Number} w - width of canvas, overflowed content will be hidden
 * @property {Number} h - height of canvas, overflowed content will be hidden
 * @property {Number} ox - Display origin x
 * @property {Number} oy - Display origin y
 * @property {Bitset} surplusDirection - bitset that represent which direction
 *                                       has overflowed item.
 *                                       Range: 0000-1111(Up/Right/Left/Down)
 */
class SpriteCanvas extends Sprite{
  /**-------------------------------------------------------------------------
   * @constructor
   * @param {Rect} rect - initialize by an rect object
   *//**
   * @constructor
   * @param {Number} x - X position in app
   * @param {Number} y - Y position in app
   * @param {Number} w - width of canvas, overflowed content will be hidden
   * @param {Number} h - height of canvas, overflowed content will be hidden
   */
  constructor(x, y, w, h){
    if(isClassOf(x, Rect)){
      let rect = x;
      y = rect.x;
      w = rect.width;
      h = rect.height;
      x = rect.x;
    }
    if(validArgCount(x, y, w, h) != 4){
      throw new ArgumentError(4, validArgCount(x,y,w,h));
    }
    super(PIXI.Texture.EMPTY);
    this.setPOS(x, y);
    this.resize(w, h);
    this.surplusDirection = 0;
    this.ox = 0; this.oy = 0;
    this.lastDisplayOrigin = [0,0];
    this.applyMask();
    this.hitArea = new Rect(0, 0, w, h);
  }
  /*-------------------------------------------------------------------------*/
  get width(){return this._width;}
  get height(){return this._height;}
  /**------------------------------------------------------------------------
   * > Check whether the object is inside the visible area
   * @param {Sprite|Bitmap} obj - the DisplayObject to be checked
   * @returns {Number} - which diection it overflowed. 
   *                     8: Up, 6: Right, 4: Left, 2: Down
   */
  isObjectVisible(obj){
    let dx = obj.x - this.ox + this.lastDisplayOrigin[0] * 2;
    let dy = obj.y - this.oy + this.lastDisplayOrigin[1] * 2;
    if(dx > this.width){return 6;}
    if(dy > this.height){return 2;}
    let dw = dx + obj.width, dh = dy + obj.height;
    if(dw < 0){return 4;}
    if(dh < 0){return 8;}
    return 0;
  }
  /*-------------------------------------------------------------------------*/
  refresh(){
    this.surplusDirection = 0;
    let dox = this.ox - this.lastDisplayOrigin[0];
    let doy = this.oy - this.lastDisplayOrigin[1];
    this.children.sort((a,b) => (a.zIndex || 0) - (b.zIndex || 0));
    for(let i=0;i<this.children.length;++i){
      let sp = this.children[i];
      if(sp.static){continue;}
      let overflowDir = this.isObjectVisible(sp);
      if(overflowDir > 0){
        sp.hide();
        this.surplusDirection |= (1 << ((overflowDir - 2) / 2))
      }
      else{sp.show();}
      let dx = sp.x - dox, dy = sp.y - doy;
      sp.setPOS(dx, dy);
    }
    this.lastDisplayOrigin = [this.ox, this.oy];
  }
  /**------------------------------------------------------------------------
   * > Synchronize child properties to parent's
   */
  syncChildrenProperties(){
    for(let i=0;i<this.children.length;++i){
      this.children[i].interactive = this.isActivate();
    }
  }
  /*-------------------------------------------------------------------------*/
  resize(w, h){
    if(w === null){w = this._width;}
    if(h === null){w = this._height;}
    this._width  = w;
    this._height = h;
    this.drawMask();
    this.hitArea = new Rect(0, 0, w, h);
    return this;
  }
  /**-------------------------------------------------------------------------
   * > Apply mask to prevent shown overflow objects
   */
  applyMask(){
    this.maskGraphics = new PIXI.Graphics();
    this.drawMask();
    this.maskGraphics.static = true;
    this.addChild(this.maskGraphics);
    this.mask = this.maskGraphics;
  }
  /*------------------------------------------------------------------------*/
  drawMask(){
    if(!this.maskGraphics){return ;}
    this.maskGraphics.clear();
    this.maskGraphics.beginFill(0xffffff);
    this.maskGraphics.drawRect(0, 0, this.width, this.height);
    this.maskGraphics.endFill();
  }
  /*------------------------------------------------------------------------*/
  clear(){
    for(let i=0;i<this.children.length;++i){
      if(this.children[i].destroy){
        this.children[i].destroy({children: true});
      }
      this.removeChild(this.children[i]);
    }
    this.children = [];
    this.applyMask();
  }
  /*------------------------------------------------------------------------*/
  sortChildren(){
    this.children.sort((a,b) => (a.zIndex || 0) - (b.zIndex || 0));
  }
  /**-------------------------------------------------------------------------
   * > Scroll window horz/vert
   */
  scroll(sx = 0, sy = 0){
    this.ox += sx;
    this.oy += sy;
    this.refresh();
  }
  /**-------------------------------------------------------------------------
   * > Set display origin
   * @param {Number} x - new ox, should be real x in pixel
   * @param {Number} y - new oy, should be rael y in pixel
   */
  setDisplayOrigin(x, y){
    this.ox = x;
    this.oy = y;
    this.refresh();
  }
  /*-------------------------------------------------------------------------*/
}

/**
 * The Superclass of all scene within the game.
 *
 * @class Scene_Base
 * @constructor
 * @extends Stage
 * @property {boolean} _active      - acitve flag
 * @property {number}  _fadingFlag  - fade type flag
 * @property {number}  _fadingTimer - timer of fade effect
 * @property {Sprite}  _fadeSprite  - sprite of fade effect
 */
class Scene_Base extends Stage{
  /**-------------------------------------------------------------------------
   * @constructor
   * @memberof Scene_Base
   */
  constructor(){
    super();
    this._active  = false;
    this._windows = [];
    this._fadingFlag = 0;
    this._fadingTimer = 0;
    this.fadeDuration = 30;
    this._buttonCooldown = new Array(0xff);
    this._fadingSprite = Graphics.fadingSprite;
    this._terminating  = false;
  }
  /**-------------------------------------------------------------------------
   * > Frame update
   * @memberof Scene_Base
   */
  update(){
    this.updateFading();
    this.updateChildren();
    this.updateShake();
  }
  /*-------------------------------------------------------------------------*/
  updateChildren(){
    this.children.forEach(function(child){
      if(child.update){
        if(this._terminating && child.isWindow){return ;}
        if(!this.overlay || !child.isWindow || child === this.overlay){
          child.update();
        }
      }
    }.bind(this))
  }
  /*------------------------------------------------------------------------*/
  updateShake(){
    if(!this._shaking){return ;}
    if(this._shakeTimer <= 0){
      this.x = 0; this.y = 0;
      this._shaking = false;
      return ;
    }
    let dis = 2 * this._shakeLevel;
    let dx = randInt(0, 2 * dis) - dis;
    let dy = randInt(0, 2 * dis) - dis;
    this.x = dx;
    this.y = dy;
    this._shakeTimer -= 1;
  }
  /*------------------------------------------------------------------------*/
  sortChildren(){
    this.children.sort((a,b) => (a.zIndex || 0) - (b.zIndex || 0));
  }
  /*-------------------------------------------------------------------------*/
  prepare(){
    // reserved
  }
  /*-------------------------------------------------------------------------*/
  shake(level = 1, duration = 30){
    this._shaking    = true;
    this._shakeLevel = level;
    this._shakeTimer = duration;
  }
  /**-------------------------------------------------------------------------
   * @returns {boolean} - whether scene is fading
   */
  isBusy(){
    return this._fadingTimer > 0;
  }
  /*-------------------------------------------------------------------------*/
  preTerminate(){
    debug_log("Scene pre-terminate: " + getClassName(this));
    this._terminating = true;
    this.fadeOutAll();
    this.deactivateChildren();
  }
  /*-------------------------------------------------------------------------*/
  terminate(){
    debug_log("Scene terminated: " + getClassName(this));
    this.disposeAllWindows();
  }
  /**-------------------------------------------------------------------------
   * > Create the components and add them to the rendering process.
   */
  create(){
    this.createBackground();
  }
  /**-------------------------------------------------------------------------
   * Deactivate all sprites to prevent interaction during terminating
   */
  deactivateChildren(){
    this.children.forEach(function(sp){
      sp.deactivate();
    })
  }
  /**-------------------------------------------------------------------------
   * > Remove windows from page
   */
  disposeAllWindows(){
    for(let i=0;i<this._windows.length;++i){
      this.disposeWindowAt(i);
    }
    this._windows = [];
  }
  /**-------------------------------------------------------------------------
   * > Remove a single window
   */
  removeWindow(win){
    this.disposeWindowAt(this._windows.indexOf(win));
  }
  /**-------------------------------------------------------------------------
   * > Dispose window
   */
  disposeWindowAt(index){
    if(index <= -1){
      console.error("Trying to dispose the window not rendered yet")
      return ;
    }
    debug_log("Dispose window: " + getClassName(this._windows[index]));
    if(Graphics.globalWindows.indexOf(this._windows[index]) == -1){
      this._windows[index].clear(true)
    }else{this._windows[index].hide()}
    this._windows.splice(index, 1);
  }
  /**-------------------------------------------------------------------------
   * > Create background
   */
  createBackground(){
    // reserved for inherited class
  }
  /**-------------------------------------------------------------------------
   * @returns {boolean} - whether current scene is active
   */
  isActive(){
    return this._active;
  }
  /*-------------------------------------------------------------------------*/
  start(){
    this._active = true;
    this._fadingSprite = Graphics.fadingSprite;
    if(DebugMode){this.addChild(Graphics.FPSSprite)}
    this.renderGlobalSprites();
    this.renderGlobalWindows();
  }
  /*-------------------------------------------------------------------------*/
  stop(){
    this._active = false;
  }
  /*-------------------------------------------------------------------------*/
  renderGlobalSprites(){
    Graphics.globalSprites.forEach(function(sp){
      Graphics.renderSprite(sp);
      if(sp.defaultActiveState){sp.activate(); sp.show();}
    });
    this.optionSprite = Graphics.optionSprite;
  }
  /*-------------------------------------------------------------------------*/
  renderGlobalWindows(){
    Graphics.globalWindows.forEach(function(win){
      Graphics.renderWindow(win);
      if(win.defaultActiveState){win.activate(); win.show();}
    });
    this.optionWindow = Graphics.optionWindow;
  }
  /*-------------------------------------------------------------------------*/
  startFadeIn(duration = this.fadeDuration){
    Graphics.renderSprite(Graphics.fadingSprite);
    this._fadingSprite.show();
    this._fadeSign = 1;
    this._fadingTimer = duration;
    this._fadingSprite.setOpacity(1);
  }
  /*-------------------------------------------------------------------------*/
  startFadeOut(duration = this.fadeDuration){
    Graphics.renderSprite(Graphics.fadingSprite);
    this._fadingSprite.show();
    this._fadeSign = -1;
    this._fadingTimer = duration;
    this._fadingSprite.setOpacity(0);
  }
  /*-------------------------------------------------------------------------*/
  updateFading(){
    if(this._fadingTimer <= 0){return ;}
    let d = this._fadingTimer;
    let opa = this._fadingSprite.opacity;
    if(this._fadeSign > 0){
      this._fadingSprite.setOpacity(opa - opa / d)
    }
    else{
      this._fadingSprite.setOpacity(opa + (1 - opa) / d)
    }
    this._fadingTimer -= 1;
    if(this._fadingTimer <= 0){this.onFadeComplete();}
  }
  /**-------------------------------------------------------------------------
   * > Fade out screen and sound
   */
  fadeOutAll(){
    Sound.fadeOutAll();
    this.startFadeOut();
  }
  /*-------------------------------------------------------------------------*/
  onFadeComplete(){
    this._fadingFlag  = 0;
    this._fadingTimer = 0;
  }
  /**-------------------------------------------------------------------------
   * @returns {number} - frames before fade completed, slower one
   */
  slowFadeSpeed(){
    return this.fadeSpeed() * 2;
  }
  /**-------------------------------------------------------------------------
   * @returns {number} - frames before fade completed
   */
  fadeSpeed(){
    return 24;
  }
  /**-------------------------------------------------------------------------
   * @returns {boolean} - Graphics is loaded and ready
   */
  isReady(){
    return Graphics.isReady();
  }
  /**-------------------------------------------------------------------------
   * > Add window to page view
   * @param {Window_Base} win - the window class
   */
  addWindow(win, forced = false){
    if(!this.isActive() && !forced){
      console.error("Trying to add window to stopped scene")
      return ;
    }
    if(win.isDisposed()){
      console.error("Try to add disposed window: " + getClassName(win));
      return ;
    }
    if(this._windows.indexOf(win) >= 0){
      return ;
    }
    this._windows.push(win);
    this.addChild(win);
  }
  /**-------------------------------------------------------------------------
   * > Pause animate sprites
   */
  pause(){
    this.children.forEach(function(sp){
      Graphics.pauseAnimatedSprite(sp);
      if(sp.isActive()){sp.lastActiveState = sp.isActive();}
      sp.deactivate();
    })
  }
  /**-------------------------------------------------------------------------
   * > Resume paused animate sprites
   */
  resume(){
    this.children.forEach(function(sp){
      Graphics.resumeAnimatedSprite(sp);
      if(sp.lastActiveState){
        sp.activate();
      }
    })
  }
  /*-------------------------------------------------------------------------*/
  heatupButton(kid){
    this._buttonCooldown[kid] = 4;
  }
  /*-------------------------------------------------------------------------*/
  isButtonCooled(kid){
    return (this._buttonCooldown[kid] || 0) == 0;
  }
  /*-------------------------------------------------------------------------*/
  raiseOverlay(ovs, fallback=null){
    if(!ovs){return ;}
    if(ovs !== this.optionWindow){
      this.optionSprite.deactivate();
      this.optionSprite.Xmark.show();
    }
    debug_log("Raise overlay: " + getClassName(ovs));
    this.overlay = ovs;
    this.overlay.oriZ = ovs.z;
    this.overlay.setZ(0x111).render();
    this.overlayFallback = fallback;
    this.children.forEach(function(sp){
      if(sp.alwaysActive){return ;}
      if(sp !== ovs){
        sp.lastActiveState = sp.isActive();
        sp.deactivate();
      }
    })
    Graphics.renderSprite(Graphics.dimSprite);
    ovs.show(); ovs.activate();
  }
  /*-------------------------------------------------------------------------*/
  closeOverlay(){
    if(!this.overlay){return ;}
    debug_log("Close overlay");
    this.optionSprite.activate();
    this.optionSprite.Xmark.hide();

    this.overlay.hide(); this.overlay.deactivate();
    this.children.forEach(function(sp){
      if(sp !== this.overlay && sp.lastActiveState){
        sp.activate();
      }
    }.bind(this))
    Graphics.removeSprite(Graphics.dimSprite);
    this.overlay.setZ(this.overlay.oriZ);
    this.overlay = null;
    if(this.overlayFallback){
      EventManager.setTimeout(()=>{
        this.overlayFallback();
        this.overlayFallback = null;
      }, 2);
    }
  }
  /*-------------------------------------------------------------------------*/
} // Scene_Base

/**---------------------------------------------------------------------------
 * The Rectangle object for abbreviation of PIXI's one
 * @class Rect
 * @extends PIXI.Rectangle
 */
class Rect extends PIXI.Rectangle{
  /**
   * @constructor
   * @param {Object} rect - initialize by the object that contain rect data
   * @param {...Number} [params] - initialize by given x, y, w, h
   * @param {Number} x - The X point of the bitmap
   * @param {Number} y - The Y point of the bitmap
   * @param {Number} width - The width of the bitmap
   * @param {Number} height - The height of the bitmap
   */
  constructor(...args){
    super(0,0,0,0);
    let arglen = validArgCount.apply(window, args);
    if(arglen == 1){
      this.x = args[0].x;
      this.y = args[0].y;
      this.width = args[0].width;
      this.height = args[0].height;
    }
    else if(arglen == 4){
      this.x = args[0];
      this.y = args[1];
      this.width = args[2];
      this.height = args[3];
    }
    else{
      throw new ArgumentError([1,4], arglen)
    }
  }
}