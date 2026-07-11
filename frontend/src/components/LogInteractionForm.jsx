import { useSelector, useDispatch } from 'react-redux'
import { useState } from 'react'
import { setSaveStatus } from '../store/interactionSlice'
import { saveInteraction } from '../api/client'

const isChanged = (field, changedFields) => changedFields.includes(field)

function Field({ id, label, value, changedFields, children }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {children}
    </div>
  )
}

export default function LogInteractionForm() {
  const dispatch = useDispatch()
  const { form, lastChangedFields, saveStatus } = useSelector((s) => s.interaction)
  const [error, setError] = useState(null)

  const cls = (field) => `field-input${isChanged(field, lastChangedFields) ? ' field-highlight' : ''}`

  const handleSave = async () => {
    setError(null)
    dispatch(setSaveStatus('saving'))
    try {
      await saveInteraction(form)
      dispatch(setSaveStatus('saved'))
    } catch (e) {
      dispatch(setSaveStatus('error'))
      setError('Could not save interaction. Is the backend running?')
    }
  }

  return (
    <section className="panel">
      <div className="form-panel-scroll scrollbar-thin">
        <h1 className="form-title">Log HCP Interaction</h1>

        <div className="section-label">Interaction Details</div>
        <div className="field-row">
          <Field id="hcp_name" label="HCP Name">
            <input
              id="hcp_name"
              className={cls('hcp_name')}
              value={form.hcp_name}
              placeholder="Search or select HCP..."
              readOnly
            />
          </Field>
          <Field id="interaction_type" label="Interaction Type">
            <select id="interaction_type" className={`field-select${isChanged('interaction_type', lastChangedFields) ? ' field-highlight' : ''}`} value={form.interaction_type} disabled>
              <option>Meeting</option>
              <option>Call</option>
              <option>Email</option>
              <option>Conference</option>
            </select>
          </Field>
        </div>

        <div className="field-row">
          <Field id="date" label="Date">
            <input id="date" type="date" className={cls('date')} value={form.date} readOnly />
          </Field>
          <Field id="time" label="Time">
            <input id="time" type="time" className={cls('time')} value={form.time} readOnly />
          </Field>
        </div>

        <Field id="attendees" label="Attendees">
          <input
            id="attendees"
            className={cls('attendees')}
            value={form.attendees}
            placeholder="Enter names or search..."
            readOnly
          />
        </Field>

        <Field id="topics_discussed" label="Topics Discussed">
          <textarea
            id="topics_discussed"
            className={`field-textarea${isChanged('topics_discussed', lastChangedFields) ? ' field-highlight' : ''}`}
            value={form.topics_discussed}
            placeholder="Enter key discussion points..."
            readOnly
          />
        </Field>
        <a className="voice-note-link" onClick={(e) => e.preventDefault()} href="#voice-note">
          🎙 Summarize from Voice Note (Requires Consent)
        </a>

        <div className="section-label">Materials Shared / Samples Distributed</div>
        <div className="subsection-title">Materials Shared</div>
        <div className="materials-row">
          {form.materials_shared.length === 0 ? (
            <p className="empty-note">No materials added.</p>
          ) : (
            <div className="chip-row">
              {form.materials_shared.map((m) => (
                <span className="chip" key={m}>{m}</span>
              ))}
            </div>
          )}
          <button className="ghost-btn" type="button" disabled>🔍 Search/Add</button>
        </div>

        <div className="subsection-title">Samples Distributed</div>
        <div className="materials-row">
          {form.samples_distributed.length === 0 ? (
            <p className="empty-note">No samples added.</p>
          ) : (
            <div className="chip-row">
              {form.samples_distributed.map((s) => (
                <span className="chip sample" key={s}>{s}</span>
              ))}
            </div>
          )}
          <button className="ghost-btn" type="button" disabled>+ Add Sample</button>
        </div>

        <div className="section-label">Observed/Inferred HCP Sentiment</div>
        <div className="sentiment-row">
          {['Positive', 'Neutral', 'Negative'].map((opt) => (
            <label className="sentiment-option" key={opt}>
              <input type="radio" name="sentiment" checked={form.sentiment === opt} readOnly disabled={false} onClick={(e) => e.preventDefault()} />
              {opt === 'Positive' ? '🙂' : opt === 'Neutral' ? '😐' : '🙁'} {opt}
            </label>
          ))}
        </div>

        <div className="section-label">Outcomes</div>
        <Field id="outcomes" label="">
          <textarea
            id="outcomes"
            className={`field-textarea${isChanged('outcomes', lastChangedFields) ? ' field-highlight' : ''}`}
            value={form.outcomes}
            placeholder="Key outcomes or agreements..."
            readOnly
          />
        </Field>

        <div className="section-label">Follow-up Actions</div>
        <Field id="follow_up_actions" label="">
          <textarea
            id="follow_up_actions"
            className={`field-textarea${isChanged('follow_up_actions', lastChangedFields) ? ' field-highlight' : ''}`}
            value={form.follow_up_actions}
            placeholder="Suggested or agreed next steps..."
            readOnly
          />
        </Field>
        {error && <p style={{ color: '#c0392b', fontSize: 13 }}>{error}</p>}
      </div>

      <div className="save-bar">
        {saveStatus === 'saved' && <span style={{ alignSelf: 'center', fontSize: 13, color: '#1f8a4c' }}>Saved ✓</span>}
        <button className="primary-btn" onClick={handleSave} disabled={saveStatus === 'saving'}>
          {saveStatus === 'saving' ? 'Saving...' : 'Save Interaction'}
        </button>
      </div>
    </section>
  )
}
