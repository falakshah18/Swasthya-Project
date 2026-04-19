
import React from 'react'
import ReactDOM from 'react-dom/client'
import './assets/css/style.css'

function App() {
  return (
    <div style={{padding: '2rem', fontFamily: 'Inter, Arial, sans-serif'}}>
      <h1>SwasthyaSaathi Frontend</h1>
      <p>This folder is a separate frontend scaffold for GitHub. The current production UI still lives in Django templates under <code>backend/core/templates</code>.</p>
      <p>Use the copied HTML files in <code>src/pages</code> as references while moving to React or another frontend framework.</p>
    </div>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
