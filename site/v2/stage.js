/* MATA | palco 3D
   Linguagem do piloto aprovado em 15/10/2026: trilho verde fosco (a empresa),
   módulo lilás acetinado (pessoas da MATA), módulo de vidro suave (inteligência artificial)
   e peças claras para o trabalho da semana. */
(function () {
  "use strict";
  var T = window.THREE;
  if (T && T.ColorManagement) T.ColorManagement.legacyMode = false;

  var COLORS = {
    green: 0x0b3f2f,
    lilac: 0xbab3e0,
    tile: 0xf2f3f7,
    glassTint: 0xe9fff7,
    mint: 0x8ff0cf
  };

  function roundedShape(w, d, r, tab) {
    var s = new T.Shape();
    var x = -w / 2, y = -d / 2;
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

  function roundedPath(w, d, r) {
    var p = new T.Path();
    var x = -w / 2, y = -d / 2;
    p.moveTo(x + r, y);
    p.quadraticCurveTo(x, y, x, y + r);
    p.lineTo(x, y + d - r);
    p.quadraticCurveTo(x, y + d, x + r, y + d);
    p.lineTo(x + w - r, y + d);
    p.quadraticCurveTo(x + w, y + d, x + w, y + d - r);
    p.lineTo(x + w, y + r);
    p.quadraticCurveTo(x + w, y, x + w - r, y);
    p.lineTo(x + r, y);
    return p;
  }

  function slab(shape, height, bevel) {
    var g = new T.ExtrudeGeometry(shape, {
      depth: Math.max(0.01, height - 2 * bevel),
      bevelEnabled: true,
      bevelThickness: bevel,
      bevelSize: bevel * 0.85,
      bevelSegments: 8,
      curveSegments: 28
    });
    g.rotateX(-Math.PI / 2);
    g.translate(0, bevel, 0);
    g.computeVertexNormals();
    return g;
  }

  function studioEnvironment(renderer) {
    var room = new T.Scene();
    var box = new T.Mesh(new T.BoxGeometry(30, 16, 30), new T.MeshBasicMaterial({ color: 0xe9e8f2, side: T.BackSide }));
    box.position.y = 6;
    room.add(box);
    function panel(w, h, intensity, color, pos, look) {
      var m = new T.Mesh(new T.PlaneGeometry(w, h), new T.MeshBasicMaterial({ color: color || 0xffffff, side: T.DoubleSide }));
      m.material.color.multiplyScalar(intensity);
      m.position.set(pos[0], pos[1], pos[2]);
      m.lookAt(look[0], look[1], look[2]);
      room.add(m);
    }
    panel(14, 6, 4.2, 0xffffff, [0, 13.5, 0], [0, 0, 0]);
    panel(3, 12, 3.2, 0xffffff, [-14, 6, 4], [0, 2, 0]);
    panel(3, 12, 2.4, 0xf2efff, [14, 6, -3], [0, 2, 0]);
    panel(10, 2.2, 2.2, 0xffffff, [3, 5, 14], [0, 1, 0]);
    panel(8, 3, 1.4, 0xd9fff1, [-6, 1.5, -14], [0, 1, 0]);
    var pmrem = new T.PMREMGenerator(renderer);
    var env = pmrem.fromScene(room, 0.035).texture;
    pmrem.dispose();
    return env;
  }

  function build(scene) {
    var M = {
      green: new T.MeshPhysicalMaterial({ color: COLORS.green, roughness: 0.72, metalness: 0.0, clearcoat: 0.08, clearcoatRoughness: 0.7, envMapIntensity: 0.55 }),
      lilac: new T.MeshPhysicalMaterial({ color: COLORS.lilac, roughness: 0.34, metalness: 0.32, clearcoat: 0.35, clearcoatRoughness: 0.35, envMapIntensity: 1.1 }),
      tile: new T.MeshPhysicalMaterial({ color: COLORS.tile, roughness: 0.42, metalness: 0.05, clearcoat: 0.5, clearcoatRoughness: 0.3 }),
      glass: new T.MeshPhysicalMaterial({ color: COLORS.glassTint, roughness: 0.14, metalness: 0, transmission: 1, thickness: 0.9, ior: 1.42, attenuationColor: new T.Color(0xa7ead6), attenuationDistance: 2.2, clearcoat: 1, clearcoatRoughness: 0.12, specularIntensity: 1, envMapIntensity: 1.25 })
    };
    var obj = {};

    var rail = new T.Group();
    var frameShape = roundedShape(8.6, 2.2, 0.42);
    frameShape.holes.push(roundedPath(8.0, 1.6, 0.22));
    var frame = new T.Mesh(slab(frameShape, 1.0, 0.09), M.green);
    var plate = new T.Mesh(slab(roundedShape(11.2, 2.2, 0.42), 0.34, 0.08), M.green);
    plate.position.x = 1.3;
    plate.position.y = -0.02;
    frame.castShadow = frame.receiveShadow = plate.castShadow = plate.receiveShadow = true;
    rail.add(plate, frame);
    rail.position.y = 0;
    scene.add(rail);
    obj.rail = rail;

    function piece(mat, w, d, h, tab, tabDir) {
      var g = slab(roundedShape(w, d, 0.3, tab), h, Math.min(0.14, h * 0.3));
      if (tabDir === -1) g.rotateY(Math.PI);
      var m = new T.Mesh(g, mat);
      m.castShadow = true;
      m.receiveShadow = true;
      var holder = new T.Group();
      holder.add(m);
      scene.add(holder);
      return holder;
    }
    obj.L = piece(M.lilac, 1.55, 1.3, 0.78, { w: 0.34, h: 0.62, f: 0.1 }, 1);
    obj.G = piece(M.glass, 1.95, 1.55, 0.82, { w: 0.42, h: 0.62, f: 0.12 }, -1);
    obj.G.children[0].castShadow = false;
    obj.A = piece(M.tile, 1.7, 1.3, 0.5);
    obj.S = piece(M.tile, 1.7, 1.3, 0.5);
    obj.P = piece(M.tile, 1.7, 1.3, 0.5);
    obj.R = piece(M.glass, 0.62, 0.62, 0.34);
    obj.R.children[0].castShadow = false;

    var glow = new T.PointLight(COLORS.mint, 3.2, 4.2, 2);
    glow.position.set(0, 0.25, 0);
    obj.G.add(glow);
    obj.glow = glow;
    return obj;
  }

  /* Estados: posição [x,y,z], rotação Y, inclinação X, escala */
  var BASE_Y = 0.32;
  function at(x, y, z, ry, rx, s) { return { p: [x, y, z], ry: ry || 0, rx: rx || 0, s: s === undefined ? 1 : s }; }
  var HIDE_L = at(-3, 2.6, 0.4, 0.4, 0, 0.001);
  var HIDE_G = at(6.6, 2.6, 0.4, -0.4, 0, 0.001);
  var HIDE_R = at(-1, 1.6, 0, 0, 0, 0.001);
  var PILE = { A: at(-3.05, BASE_Y, 0.05, 0.22, 0), S: at(-2.85, BASE_Y + 0.5, 0.18, -0.38, 0.05), P: at(-3.1, BASE_Y + 1.0, -0.06, 0.62, -0.06) };
  var PILE2 = { A: at(-0.95, BASE_Y, 0.05, 0.22, 0), S: at(-0.8, BASE_Y + 0.5, 0.18, -0.38, 0.05), P: at(-1.05, BASE_Y + 1.0, -0.06, 0.62, -0.06) };
  var SL = at(-3.05, BASE_Y, 0, 0, 0);
  var DOCK = at(5.55, BASE_Y, 0, 0, 0);

  var STATES = {
    antes: { L: HIDE_L, G: HIDE_G, R: HIDE_R, A: PILE.A, S: PILE.S, P: PILE.P, glow: 0, cam: [[3, 12, 11], [-1.2, 0.3, 0]] },
    shadowing: { L: SL, G: HIDE_G, R: HIDE_R, A: PILE2.A, S: PILE2.S, P: PILE2.P, glow: 0, cam: [[3.5, 12, 12], [-0.5, 0.3, 0]] },
    memoria: { L: SL, G: DOCK, R: HIDE_R, A: PILE2.A, S: PILE2.S, P: PILE2.P, glow: 1, cam: [[5, 13, 13], [1.2, 0, 0]] },
    planejada: { L: SL, G: DOCK, R: HIDE_R, A: at(3, BASE_Y, 0), S: at(1, BASE_Y, 0), P: at(-1, BASE_Y, 0), glow: 1, cam: [[5, 13, 13], [1.2, 0, 0]] },
    rpm: { L: SL, G: DOCK, R: HIDE_R, A: at(-1, BASE_Y, 0), S: at(1, BASE_Y, 0), P: at(3, BASE_Y, 0), glow: 1, cam: [[5, 13, 13], [1.2, 0, 0]], arc: { A: 1.6, P: 0.9 } },
    apresentacao: { L: SL, G: DOCK, R: HIDE_R, A: at(-1, BASE_Y + 1.05, 0.55, 0.1, 0.45), S: at(1, BASE_Y, 0), P: at(3, BASE_Y, 0), glow: 1, cam: [[3.5, 10.5, 11.5], [0, 0.6, 0]] },
    retorno: { L: SL, G: DOCK, R: at(-3.05, BASE_Y + 0.95, 0, 0, 0), A: at(-1, BASE_Y, 0), S: at(1, BASE_Y, 0), P: at(3, BASE_Y, 0), glow: 1, cam: [[3.5, 12, 12.5], [-0.6, 0.3, 0]] },
    final: { L: SL, G: DOCK, R: HIDE_R, A: at(-1, BASE_Y, 0), S: at(1, BASE_Y, 0), P: at(3, BASE_Y, 0), glow: 1.15, cam: [[5.5, 13.5, 13.5], [1.3, 0, 0]] },
    hero: { L: SL, G: DOCK, R: HIDE_R, A: at(-1, BASE_Y, 0), S: at(1, BASE_Y, 0), P: at(3, BASE_Y, 0), glow: 1.1, cam: [[7.5, 11.5, 17.5], [1.3, -0.4, 0]] },
    heroMobile: { L: SL, G: DOCK, R: HIDE_R, A: at(-1, BASE_Y, 0), S: at(1, BASE_Y, 0), P: at(3, BASE_Y, 0), glow: 1.1, cam: [[4.6, 9.6, 15.5], [1.3, 0.2, 0]] }
  };

  function Stage(host, opts) {
    this.host = host;
    this.canvas = host.querySelector("canvas");
    this.labelsEl = host.querySelector(".labels");
    this.opts = opts || {};
    this.reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    this.labels = [];
    this.state = null;
    this.visible = true;
    this.t0 = performance.now();
    this.arcT = 1;
    this.init();
  }

  Stage.prototype.init = function () {
    var r = new T.WebGLRenderer({ canvas: this.canvas, antialias: true, alpha: false, powerPreference: "high-performance" });
    r.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    r.outputEncoding = T.sRGBEncoding;
    r.toneMapping = T.ACESFilmicToneMapping;
    r.toneMappingExposure = 1.05;
    r.shadowMap.enabled = true;
    r.shadowMap.type = T.VSMShadowMap;
    this.renderer = r;
    var scene = new T.Scene();
    var bg = new T.Color(this.opts.background || 0xeceef5);
    scene.background = bg;
    this.scene = scene;
    scene.environment = studioEnvironment(r);

    var floor = new T.Mesh(new T.PlaneGeometry(80, 80), new T.ShadowMaterial({ opacity: 0.16, color: 0x2a2450 }));
    floor.rotation.x = -Math.PI / 2;
    floor.receiveShadow = true;
    scene.add(floor);

    var key = new T.DirectionalLight(0xffffff, 1.1);
    key.position.set(-4, 12, 7);
    key.castShadow = true;
    key.shadow.mapSize.set(2048, 2048);
    key.shadow.camera.left = -10; key.shadow.camera.right = 10;
    key.shadow.camera.top = 8; key.shadow.camera.bottom = -8;
    key.shadow.camera.near = 1; key.shadow.camera.far = 30;
    key.shadow.radius = 14;
    key.shadow.blurSamples = 20;
    key.shadow.bias = -0.0004;
    scene.add(key);
    scene.add(new T.HemisphereLight(0xf4f2ff, 0xdfe6e2, 0.35));

    this.obj = build(scene);
    this.camera = new T.PerspectiveCamera(28, 1, 0.1, 100);
    this.camPos = new T.Vector3(); this.camLook = new T.Vector3();
    this.items = ["L", "G", "R", "A", "S", "P"];
    this.go(this.opts.state || "antes", true);
    this.resize();
    var self = this;
    window.addEventListener("resize", function () { self.resize(); });
    if ("IntersectionObserver" in window) {
      new IntersectionObserver(function (es) { self.visible = es[0].isIntersecting; if (self.visible) self.loop(); }, { rootMargin: "120px" }).observe(this.host);
    }
    this.loop();
  };

  Stage.prototype.resize = function () {
    var w = this.host.clientWidth, h = this.host.clientHeight;
    if (!w || !h) return;
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    var shift = (this.opts.shift && w >= 900) ? this.opts.shift : 0;
    if (shift) this.camera.setViewOffset(w, h, -w * shift, 0, w, h); else this.camera.clearViewOffset();
    this.camera.updateProjectionMatrix();
    if (this.opts.responsive) {
      var narrow = w < 640;
      var want = narrow ? this.opts.responsive[1] : this.opts.responsive[0];
      if (want !== this.state) this.go(want, true);
    } else if (this.state) {
      this.go(this.state, !this.started);
    }
    this.started = true;
    this.render();
  };

  Stage.prototype.go = function (name, snap) {
    var st = STATES[name];
    if (!st) return;
    var prev = this.state;
    this.state = name;
    var self = this;
    this.target = {};
    this.items.forEach(function (k) {
      var s = st[k];
      var q = new T.Quaternion().setFromEuler(new T.Euler(s.rx, s.ry, 0, "YXZ"));
      self.target[k] = { p: new T.Vector3(s.p[0], s.p[1], s.p[2]), q: q, s: s.s };
    });
    this.arc = st.arc || null;
    this.arcT = 0;
    this.targetGlow = st.glow;
    this.targetCam = [new T.Vector3().fromArray(st.cam[0]), new T.Vector3().fromArray(st.cam[1])];
    var asp = this.host.clientWidth / Math.max(1, this.host.clientHeight);
    var fit = Math.max(1, 1.2 / Math.max(0.4, asp)) * (this.opts.camScale || 1);
    this.targetCam[0].sub(this.targetCam[1]).multiplyScalar(fit).add(this.targetCam[1]);
    if (snap || this.reduce || !prev) {
      this.items.forEach(function (k) {
        var o = self.obj[k], t = self.target[k];
        o.position.copy(t.p); o.quaternion.copy(t.q); o.scale.setScalar(t.s);
      });
      this.obj.glow.intensity = 3.2 * this.targetGlow;
      this.camPos.copy(this.targetCam[0]); this.camLook.copy(this.targetCam[1]);
      this.arcT = 1;
    }
    this.loop();
  };

  Stage.prototype.setLabels = function (list) {
    var el = this.labelsEl;
    if (!el) return;
    var self = this;
    this.labels.forEach(function (l) { l.node.classList.remove("on"); var n = l.node; setTimeout(function () { if (!n.classList.contains("on")) n.remove(); }, 400); });
    this.labels = (list || []).map(function (l) {
      var n = document.createElement("div");
      n.className = "tag3d" + (l.kind ? " " + l.kind : "");
      n.innerHTML = '<div class="c"><b>' + l.t + "</b>" + (l.s ? "<span>" + l.s + "</span>" : "") + "</div>";
      el.appendChild(n);
      requestAnimationFrame(function () { n.classList.add("on"); });
      return { node: n, obj: l.o, dy: l.dy || 0, dx: l.dx || 0, dz: l.dz || 0, side: l.side || "up" };
    });
    this.render();
  };

  Stage.prototype.loop = function () {
    if (this.raf) return;
    var self = this;
    var last = performance.now();
    function frame(now) {
      self.raf = null;
      var dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      var moving = self.step(dt, now);
      self.render();
      if (self.visible && (moving || self.opts.idle)) self.raf = requestAnimationFrame(frame);
    }
    this.raf = requestAnimationFrame(frame);
  };

  Stage.prototype.step = function (dt, now) {
    var k = this.reduce ? 1 : 1 - Math.exp(-dt * 4.2);
    var self = this, moving = false;
    if (this.arcT < 1) this.arcT = Math.min(1, this.arcT + dt * 0.9);
    this.items.forEach(function (key) {
      var o = self.obj[key], t = self.target[key];
      var tp = t.p.clone();
      if (self.arc && self.arc[key] && self.arcT < 1) tp.y += Math.sin(Math.PI * Math.min(1, self.arcT * 1.15)) * self.arc[key];
      if (o.position.distanceToSquared(tp) > 1e-6 || Math.abs(o.scale.x - t.s) > 1e-4 || o.quaternion.angleTo(t.q) > 1e-4) moving = true;
      o.position.lerp(tp, k);
      o.quaternion.slerp(t.q, k);
      o.scale.setScalar(o.scale.x + (t.s - o.scale.x) * k);
    });
    if (this.arcT < 1) moving = true;
    this.obj.glow.intensity += (3.2 * this.targetGlow - this.obj.glow.intensity) * k;
    if (this.camPos.distanceToSquared(this.targetCam[0]) > 1e-5) moving = true;
    this.camPos.lerp(this.targetCam[0], k * 0.8);
    this.camLook.lerp(this.targetCam[1], k * 0.8);
    if (this.opts.idle && !this.reduce) {
      var tt = (now - this.t0) / 1000;
      this.obj.G.children[0].position.y = Math.sin(tt * 1.1) * 0.035;
    }
    return moving;
  };

  Stage.prototype.render = function () {
    var cam = this.camera;
    cam.position.copy(this.camPos);
    cam.lookAt(this.camLook);
    this.renderer.render(this.scene, cam);
    var w = this.host.clientWidth, h = this.host.clientHeight;
    var v = new T.Vector3();
    var self = this;
    this.labels.forEach(function (l) {
      var o = self.obj[l.obj];
      if (!o) return;
      v.copy(o.position);
      v.x += l.dx; v.z += l.dz;
      v.y += (l.obj === "rail" ? 0.9 : 0.9) + l.dy;
      v.project(cam);
      var x = (v.x * 0.5 + 0.5) * w, y = (-v.y * 0.5 + 0.5) * h;
      var hidden = l.obj !== "rail" && o.scale.x < 0.5;
      l.node.style.transform = "translate(" + x.toFixed(1) + "px," + y.toFixed(1) + "px)";
      l.node.style.visibility = hidden ? "hidden" : "visible";
    });
  };

  function supported() {
    if (!T) return false;
    try { var c = document.createElement("canvas"); return !!(c.getContext("webgl2") || c.getContext("webgl")); } catch (e) { return false; }
  }

  window.MataStage = { Stage: Stage, supported: supported };
})();
