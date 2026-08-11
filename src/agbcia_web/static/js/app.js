import { createBoxPreview } from './preview3d.js';
import { applyBlobToImg, debounce } from './preview-utils.js';
import { DropZone } from './drop-zone.js';

const { createApp } = Vue;

createApp({
  data() {
    return {
      config: { save_types: [], result_ttl_seconds: 0 },
      mode: 'native',
      files: { rom: null, icon: null, bannerImage: null, badge: null, sound: null },
      defaults: { titleName: '', titleId: '' },
      form: {
        titleName: '',
        titleId: '',
        longTitle: '',
        publisher: '',
        saveType: '',
        rtcPresent: '',
        productCode: '',
        titleVersion: 1,
        boxShellColor: 'd0d0d8',
      },
      audioUrl: 'templates/audio-template.wav',
      audioPlaying: false,
      building: false,
      buildError: null,
      buildResult: null,
    };
  },

  computed: {
    downloadUrl() {
      return this.buildResult ? `/api/download/${this.buildResult.token}` : null;
    },
    qrUrl() {
      return this.buildResult ? `/api/download/${this.buildResult.token}/qr` : null;
    },
    canBuild() {
      return Boolean(
        this.files.rom &&
        this.files.icon &&
        this.files.bannerImage &&
        this.form.titleName &&
        this.form.titleId &&
        !this.building
      );
    },
  },

  created() {
    this._debouncedIconSmall = debounce((file) => this.applyCropPreview('icon_small', file, 'iconSmallImg'), 250);
    this._debouncedIconLarge = debounce((file) => this.applyCropPreview('icon_large', file, 'iconLargeImg'), 250);
    this._debouncedBoxArt = debounce((file) => this.applyBoxArtPreview(file), 250);
    this._debouncedBadge = debounce((file) => this.applyCropPreview('badge', file, 'badgeImg'), 250);
  },

  async mounted() {
    const res = await fetch('/api/config');
    this.config = await res.json();
    this.box = createBoxPreview(this.$refs.boxCanvas);
    this.box.setShellColor(this.form.boxShellColor);
  },

  beforeUnmount() {
    this.box?.dispose();
    if (this._audioObjectUrl) URL.revokeObjectURL(this._audioObjectUrl);
  },

  methods: {
    async onRomChange(file) {
      this.files.rom = file;
      if (!file) return;

      const body = new FormData();
      body.append('rom', file);
      const res = await fetch('/api/preview/rom-info', { method: 'POST', body });
      if (!res.ok) return;
      const payload = await res.json();

      this.defaults.titleName = payload.suggested_title_name || payload.title;
      this.defaults.titleId = payload.suggested_title_id;
      this.form.titleName = this.defaults.titleName;
      this.form.titleId = this.defaults.titleId;
      this.form.longTitle = this.defaults.titleName;
      this.form.productCode = payload.suggested_product_code;
    },

    resetTitleName() {
      this.form.titleName = this.defaults.titleName;
    },
    resetTitleId() {
      this.form.titleId = this.defaults.titleId;
    },

    onIconChange(file) {
      this.files.icon = file;
      if (!file) return;
      this._debouncedIconSmall(file);
      this._debouncedIconLarge(file);
    },

    onBannerImageChange(file) {
      this.files.bannerImage = file;
      if (file) this._debouncedBoxArt(file);
    },

    onBadgeChange(file) {
      this.files.badge = file;
      if (file) this._debouncedBadge(file);
    },

    onSoundChange(file) {
      this.files.sound = file;
      if (this._audioObjectUrl) {
        URL.revokeObjectURL(this._audioObjectUrl);
        this._audioObjectUrl = null;
      }
      if (file) {
        this.audioUrl = this._audioObjectUrl = URL.createObjectURL(file);
      } else {
        this.audioUrl = 'templates/audio-template.wav';
      }
      this.audioPlaying = false;
    },

    toggleAudio() {
      const audio = this.$refs.audioEl;
      if (this.audioPlaying) {
        audio.pause();
      } else {
        audio.play();
      }
      this.audioPlaying = !this.audioPlaying;
    },

    onShellColorInput() {
      this.box.setShellColor(this.form.boxShellColor);
    },

    async applyCropPreview(kind, file, refName) {
      const body = new FormData();
      body.append('kind', kind);
      body.append('image', file);
      const res = await fetch('/api/preview/crop', { method: 'POST', body });
      if (res.ok) applyBlobToImg(this.$refs[refName], await res.blob());
    },

    async applyBoxArtPreview(file) {
      const body = new FormData();
      body.append('kind', 'box_art');
      body.append('image', file);
      const res = await fetch('/api/preview/crop', { method: 'POST', body });
      if (!res.ok) return;
      const url = applyBlobToImg(this.$refs.boxArtImg, await res.blob());
      this.box.setBoxArtTexture(url);
    },

    async submitBuild() {
      this.building = true;
      this.buildError = null;
      this.buildResult = null;
      try {
        const body = new FormData();
        body.append('mode', this.mode);
        body.append('title_name', this.form.titleName);
        body.append('title_id', this.form.titleId);
        if (this.form.longTitle) body.append('long_title', this.form.longTitle);
        body.append('publisher', this.form.publisher);
        if (this.form.saveType) body.append('save_type', this.form.saveType);
        if (this.form.rtcPresent) body.append('rtc_present', this.form.rtcPresent);
        if (this.form.productCode) body.append('product_code', this.form.productCode);
        body.append('title_version', this.form.titleVersion);
        body.append('box_shell_color', this.form.boxShellColor);
        body.append('rom', this.files.rom);
        body.append('icon', this.files.icon);
        body.append('banner_image', this.files.bannerImage);
        if (this.files.badge) body.append('bottom_badge', this.files.badge);
        if (this.files.sound) body.append('banner_sound', this.files.sound);

        const res = await fetch('/api/build', { method: 'POST', body });
        const payload = await res.json();
        if (!res.ok) throw new Error(payload.message);
        this.buildResult = payload;
      } catch (err) {
        this.buildError = err.message;
      } finally {
        this.building = false;
      }
    },
  },
})
  .component('drop-zone', DropZone)
  .mount('#app');
