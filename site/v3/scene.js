/* MATA | abertura 3D
   Bloco verde fosco (a empresa), módulo lilás acetinado (pessoas da MATA) e módulo de vidro suave (inteligência artificial).
   As peças começam separadas e se acoplam conforme a leitura avança. */
(function () {
  "use strict";
  var T = window.THREE;
  if (T && T.ColorManagement) T.ColorManagement.legacyMode = false;

  function rounded(w, d, r, tab) {
    var s = new T.Shape(), x = -w / 2, y = -d / 2;
    s.moveTo(x + r, y);
    s.lineTo(x + w - r, y);
    s.quadraticCurveTo(x + w, y, x + w, y + r);
    if (tab) {
      var th = tab.h / 2, f = Math.min(tab.f, th);
      s.lineTo(x + w, -th - f);
      s.quadraticCurveTo(x + w, -th, x + w + f, -th);
      s.lineTo(x + w + tab.w - f, -th);
      s.quadraticCurveTo(x + w + tab.w, -th, x + w + tab.w, -th + f);
      s.lineTo(x + w + tab.w, th - f);
      s.quadraticCurveTo(x + w + tab.w, th, x + w + tab.w - f, th);
      s.lineTo(x + w + f, th);
      s.quadraticCurveTo(x + w, th, x + w, th + f);
    }
    s.lineTo(x + w, y + d - r);
    s.quadraticCurveTo(x + w, y + d, x + w - r, y + d);
    s.lineTo(x + r, y + d);
    s.quadraticCurveTo(x, y + d, x, y + d - r);
    s.lineTo(x, y + r);
    s.quadraticCurveTo(x, y, x + r, y);
    return s;
  }

  function slab(shape, h, bevel) {
    var g = new T.ExtrudeGeometry(shape, { depth: Math.max(0.01, h - 2 * bevel), bevelEnabled: true, bevelThickness: bevel, bevelSize: bevel * 0.85, bevelSegments: 10, curveSegments: 32 });
    g.rotateX(-Math.PI / 2);
    g.translate(0, bevel - h / 2, 0);
    g.computeVertexNormals();
    return g;
  }

  function environment(renderer) {
    var room = new T.Scene();
    room.add(new T.Mesh(new T.BoxGeometry(30, 18, 30), new T.MeshBasicMaterial({ color: 0xeceaf4, side: T.BackSide })));
    function panel(w, h, k, c, p, look) {
      var m = new T.Mesh(new T.PlaneGeometry(w, h), new T.MeshBasicMaterial({ color: c, side: T.DoubleSide }));
      m.material.color.multiplyScalar(k);
      m.position.set(p[0], p[1], p[2]);
      m.lookAt(look[0], look[1], look[2]);
      room.add(m);
    }
    panel(16, 7, 4, 0xffffff, [0, 8.5, 2], [0, 0, 0]);
    panel(3, 12, 3, 0xffffff, [-13, 2, 6], [0, 0, 0]);
    panel(3, 12, 2.4, 0xf0ecff, [13, 2, -2], [0, 0, 0]);
    panel(12, 2.4, 1.8, 0xffffff, [0, -1, 14], [0, 0, 0]);
    panel(10, 4, 1.3, 0xd6fff0, [-5, -4, -13], [0, 0, 0]);
    var pm = new T.PMREMGenerator(renderer);
    var tex = pm.fromScene(room, 0.03).texture;
    pm.dispose();
    return tex;
  }

  /* Fundo: branco gelo com um halo do gradiente oficial ao centro */
  function backdrop(img, w, h) {
    var c = document.createElement("canvas");
    c.width = 1024; c.height = Math.round(1024 * h / Math.max(1, w));
    var g = c.getContext("2d");
    g.fillStyle = "#F1F2F6";
    g.fillRect(0, 0, c.width, c.height);
    if (img && img.complete && img.naturalWidth) {
      var off = document.createElement("canvas");
      off.width = c.width; off.height = c.height;
      var o = off.getContext("2d");
      o.drawImage(img, 0, 0, off.width, off.height);
      o.globalCompositeOperation = "destination-in";
      var rg = o.createRadialGradient(c.width / 2, c.height * 0.56, 0, c.width / 2, c.height * 0.56, Math.max(c.width, c.height) * 0.48);
      rg.addColorStop(0, "rgba(0,0,0,.78)");
      rg.addColorStop(0.55, "rgba(0,0,0,.32)");
      rg.addColorStop(1, "rgba(0,0,0,0)");
      o.fillStyle = rg;
      o.fillRect(0, 0, off.width, off.height);
      g.drawImage(off, 0, 0);
    }
    var t = new T.CanvasTexture(c);
    t.encoding = T.sRGBEncoding;
    return t;
  }

  function at(x, y, z, rx, ry, rz, s) { return { p: new T.Vector3(x, y, z), q: new T.Quaternion().setFromEuler(new T.Euler(rx || 0, ry || 0, rz || 0)), s: s === undefined ? 1 : s }; }

  /* Estados de leitura */
  var STATES = [
    { green: at(0, -2.6, -0.4, 0.2, 0.3, 0, 0.001), lilac: at(-2.2, 0.15, 0, 0.42, 0.55, -0.12), glass: at(2.25, 0.35, 0.2, 0.5, -0.6, 0.14), seeds: 0, glow: 0.35, cam: [0, 1.4, 13.5] },
    { green: at(0, -0.62, 0, 0.32, -0.42, 0), lilac: at(-1.24, 0.2, 0, 0.32, -0.42, 0), glass: at(1.3, 0.2, 0, 0.32, -0.42, 0), seeds: 0, glow: 0.8, cam: [0, 1.2, 13.4] },
    { green: at(0, -0.62, 0, 0.36, -0.7, 0), lilac: at(-1.24, 0.2, 0, 0.36, -0.7, 0), glass: at(1.3, 0.2, 0, 0.36, -0.7, 0), seeds: 0, glow: 1.6, cam: [0.3, 1.3, 12.4] },
    { green: at(0, -0.62, 0, 0.5, -0.25, 0), lilac: at(-1.24, 0.24, -0.34, 0.5, -0.25, 0), glass: at(1.3, 0.24, -0.34, 0.5, -0.25, 0), seeds: 3, glow: 1.2, cam: [0, 1.6, 13.8] }
  ];

  function Scene(host, opts) {
    this.host = host;
    this.opts = opts || {};
    this.reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    this.index = -1;
    this.pointer = { x: 0, y: 0, tx: 0, ty: 0 };
    this.t0 = performance.now();
    this.setup();
  }

  Scene.prototype.setup = function () {
    var canvas = this.host.querySelector("canvas");
    var r = new T.WebGLRenderer({ canvas: canvas, antialias: true, powerPreference: "high-performance" });
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.outputEncoding = T.sRGBEncoding;
    r.toneMapping = T.ACESFilmicToneMapping;
    r.toneMappingExposure = 1.02;
    this.renderer = r;
    var scene = new T.Scene();
    this.scene = scene;
    scene.environment = environment(r);
    var M = {
      green: new T.MeshPhysicalMaterial({ color: 0x0b3f2f, roughness: 0.74, metalness: 0, clearcoat: 0.06, clearcoatRoughness: 0.8, envMapIntensity: 0.55 }),
      lilac: new T.MeshPhysicalMaterial({ color: 0xbdb5e4, roughness: 0.32, metalness: 0.3, clearcoat: 0.4, clearcoatRoughness: 0.3, envMapIntensity: 1.1 }),
      glass: new T.MeshPhysicalMaterial({ color: 0xf2fffa, roughness: 0.07, transmission: 1, thickness: 1.5, ior: 1.45, attenuationColor: new T.Color(0x86dcc2), attenuationDistance: 1.5, clearcoat: 1, clearcoatRoughness: 0.06, specularIntensity: 1, envMapIntensity: 1.6 }),
      seed: new T.MeshPhysicalMaterial({ color: 0xf3f4f8, roughness: 0.4, clearcoat: 0.5, clearcoatRoughness: 0.3 })
    };
    var self = this;
    function group(mesh) { var g = new T.Group(); g.add(mesh); scene.add(g); return g; }
    this.green = group(new T.Mesh(slab(rounded(4.9, 2.3, 0.55), 0.95, 0.2), M.green));
    var lg = slab(rounded(2.1, 1.75, 0.42), 0.82, 0.16);
    this.lilac = group(new T.Mesh(lg, M.lilac));
    var gg = slab(rounded(2.25, 1.85, 0.46, { w: 0.42, h: 0.72, f: 0.12 }), 0.86, 0.17);
    gg.rotateY(Math.PI);
    this.glass = group(new T.Mesh(gg, M.glass));
    this.glow = new T.PointLight(0x8ff0cf, 0, 5, 2);
    this.glow.position.set(-0.6, -0.2, 0);
    this.glass.add(this.glow);
    this.seeds = [];
    var seedGeo = slab(rounded(0.9, 0.44, 0.16), 0.3, 0.08);
    var seedPos = [[-1.45, 0.63, 0.84], [0, 0.63, 0.84], [1.45, 0.63, 0.84]];
    var seedMat = [M.seed, M.lilac, M.glass];
    seedPos.forEach(function (p, i) {
      var m = new T.Mesh(seedGeo, seedMat[i]);
      var g = new T.Group();
      g.add(m);
      g.userData.home = new T.Vector3(p[0], p[1], p[2]);
      g.scale.setScalar(0.001);
      self.green.add(g);
      self.seeds.push(g);
    });
    var key = new T.DirectionalLight(0xffffff, 0.7);
    key.position.set(-3, 8, 6);
    scene.add(key);
    scene.add(new T.HemisphereLight(0xf6f4ff, 0xe2ebe7, 0.3));

    this.camera = new T.PerspectiveCamera(26, 1, 0.1, 100);
    this.camPos = new T.Vector3(0, 1.4, 13.5);
    this.look = new T.Vector3(0, 0, 0);

    this.gradImg = new Image();
    this.gradImg.onload = function () { self.resize(); };
    this.gradImg.src = this.opts.gradient;

    this.set(0, true);
    this.resize();
    window.addEventListener("resize", function () { self.resize(); });
    if (!this.reduce) {
      window.addEventListener("pointermove", function (e) {
        self.pointer.tx = (e.clientX / window.innerWidth - 0.5);
        self.pointer.ty = (e.clientY / window.innerHeight - 0.5);
      }, { passive: true });
    }
    this.running = true;
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { self.running = es[0].isIntersecting; if (self.running) self.loop(); }).observe(this.host);
    }
    this.loop();
  };

  Scene.prototype.resize = function () {
    var w = this.host.clientWidth, h = this.host.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    /* em telas estreitas, afasta a câmera para caber o conjunto */
    this.fit = Math.max(1, 1.25 / (w / h));
    this.camera.updateProjectionMatrix();
    if (this.scene.background && this.scene.background.dispose) this.scene.background.dispose();
    this.scene.background = backdrop(this.gradImg, w, h);
    this.draw(0);
  };

  Scene.prototype.set = function (i, snap) {
    i = Math.max(0, Math.min(STATES.length - 1, i));
    if (i === this.index && !snap) return;
    this.index = i;
    this.target = STATES[i];
    if (snap || this.reduce) {
      var t = this.target, self = this;
      ["green", "lilac", "glass"].forEach(function (k) { self[k].position.copy(t[k].p); self[k].quaternion.copy(t[k].q); self[k].scale.setScalar(t[k].s); });
      this.camPos.set(t.cam[0], t.cam[1], t.cam[2]);
      this.glow.intensity = 3 * t.glow;
      this.seeds.forEach(function (s, n) { var on = n < t.seeds; s.position.copy(s.userData.home); s.scale.setScalar(on ? 1 : 0.001); });
    }
    this.loop();
  };

  Scene.prototype.loop = function () {
    if (this.raf || !this.running) return;
    var self = this, last = performance.now();
    function frame(now) {
      self.raf = null;
      var dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      self.update(dt, now);
      self.draw(now);
      if (self.running) self.raf = requestAnimationFrame(frame);
    }
    this.raf = requestAnimationFrame(frame);
  };

  Scene.prototype.update = function (dt, now) {
    var k = this.reduce ? 1 : 1 - Math.exp(-dt * 3.2);
    var t = this.target, self = this;
    var time = (now - this.t0) / 1000;
    ["green", "lilac", "glass"].forEach(function (key, n) {
      var o = self[key], s = t[key];
      var p = s.p.clone();
      if (self.index === 0 && !self.reduce && key !== "green") {
        p.y += Math.sin(time * 0.8 + n * 1.7) * 0.12;
      }
      o.position.lerp(p, k);
      o.quaternion.slerp(s.q, k);
      o.scale.setScalar(o.scale.x + (s.s - o.scale.x) * k);
    });
    this.seeds.forEach(function (sd, n) {
      var on = n < t.seeds;
      var delay = self.reduce ? 1 : Math.max(0, Math.min(1, (self.seedClock || 0) * 1.6 - n * 0.45));
      var want = on ? delay : 0.001;
      sd.scale.setScalar(sd.scale.x + (Math.max(0.001, want) - sd.scale.x) * k);
      var drop = on ? (1 - delay) * 0.9 : 0.9;
      sd.position.set(sd.userData.home.x, sd.userData.home.y + drop, sd.userData.home.z);
    });
    this.seedClock = t.seeds ? (this.seedClock || 0) + dt : 0;
    this.glow.intensity += (3 * t.glow - this.glow.intensity) * k;
    var cam = new T.Vector3(t.cam[0], t.cam[1], t.cam[2]).multiplyScalar(this.fit || 1);
    this.camPos.lerp(cam, k * 0.7);
    this.pointer.x += (this.pointer.tx - this.pointer.x) * k * 0.6;
    this.pointer.y += (this.pointer.ty - this.pointer.y) * k * 0.6;
  };

  Scene.prototype.draw = function () {
    var c = this.camera;
    c.position.set(this.camPos.x + this.pointer.x * 1.4, this.camPos.y - this.pointer.y * 0.9, this.camPos.z);
    c.lookAt(this.look.x, this.look.y - (this.opts.lookDrop || 0), this.look.z);
    this.renderer.render(this.scene, c);
  };

  window.MataScene = {
    Scene: Scene,
    supported: function () {
      if (!T) return false;
      try { var c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); } catch (e) { return false; }
    }
  };
})();
