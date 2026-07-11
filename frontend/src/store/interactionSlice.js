import { createSlice } from '@reduxjs/toolkit'

const now = new Date()
const pad = (n) => String(n).padStart(2, '0')

export const emptyForm = {
  hcp_name: '',
  interaction_type: 'Meeting',
  date: `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}`,
  time: `${pad(now.getHours())}:${pad(now.getMinutes())}`,
  attendees: '',
  topics_discussed: '',
  materials_shared: [],
  samples_distributed: [],
  sentiment: '',
  outcomes: '',
  follow_up_actions: '',
}

const interactionSlice = createSlice({
  name: 'interaction',
  initialState: {
    form: { ...emptyForm },
    lastChangedFields: [],
    saveStatus: 'idle', // idle | saving | saved | error
  },
  reducers: {
    applyFormUpdate(state, action) {
      const { form_state, changed_fields } = action.payload
      state.form = { ...state.form, ...form_state }
      state.lastChangedFields = changed_fields || []
      state.saveStatus = 'idle'
    },
    clearHighlights(state) {
      state.lastChangedFields = []
    },
    resetForm(state) {
      state.form = { ...emptyForm }
      state.lastChangedFields = []
      state.saveStatus = 'idle'
    },
    setSaveStatus(state, action) {
      state.saveStatus = action.payload
    },
  },
})

export const { applyFormUpdate, clearHighlights, resetForm, setSaveStatus } = interactionSlice.actions
export default interactionSlice.reducer
