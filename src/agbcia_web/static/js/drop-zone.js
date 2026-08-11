/** A click-or-drag file picker. Emits `file-selected` with a File, or
 * null when cleared. */
export const DropZone = {
  props: {
    label: { type: String, required: true },
    accept: { type: String, default: '' },
    hint: { type: String, default: '' },
    description: { type: String, default: '' },
    templateUrl: { type: String, default: '' },
  },
  emits: ['file-selected'],
  data() {
    return { dragging: false, fileName: null };
  },
  methods: {
    onDrop(event) {
      this.dragging = false;
      const file = event.dataTransfer.files[0];
      if (file) this.select(file);
    },
    onPick(event) {
      const file = event.target.files[0];
      if (file) this.select(file);
    },
    select(file) {
      this.fileName = file.name;
      this.$emit('file-selected', file);
    },
    clear() {
      this.fileName = null;
      this.$refs.input.value = '';
      this.$emit('file-selected', null);
    },
  },
  template: `
    <div class="drop-zone-field">
      <div class="drop-zone"
           :class="{ dragging, filled: fileName }"
           @dragover.prevent="dragging = true"
           @dragleave.prevent="dragging = false"
           @drop.prevent="onDrop"
           @click="$refs.input.click()">
        <input ref="input" type="file" :accept="accept" hidden @change="onPick" />
        <span class="drop-zone-label">{{ label }}</span>
        <span class="drop-zone-status">{{ fileName || hint }}</span>
        <button v-if="fileName" type="button" class="drop-zone-clear" @click.stop="clear">&times;</button>
      </div>
      <p v-if="description" class="field-hint">
        {{ description }}
        <a v-if="templateUrl" :href="templateUrl" download class="template-link">[template]</a>
      </p>
    </div>
  `,
};
