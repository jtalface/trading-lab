'use client'

import { useState, useEffect } from 'react'
import { api, JournalEntry } from '@/lib/api'
import { format } from 'date-fns'

export default function JournalPage() {
  const [entries, setEntries] = useState<JournalEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showForm, setShowForm] = useState(false)
  const [editingEntry, setEditingEntry] = useState<JournalEntry | null>(null)

  const [formData, setFormData] = useState({
    date: format(new Date(), 'yyyy-MM-dd'),
    title: '',
    content: '',
    tags: '',
  })

  useEffect(() => {
    loadEntries()
  }, [])

  const loadEntries = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const data = await api.getJournalEntries({ limit: 50 })
      setEntries(data)
    } catch (err: any) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    try {
      if (editingEntry) {
        await api.updateJournalEntry(editingEntry.id, {
          title: formData.title,
          content: formData.content,
          tags: formData.tags,
        })
      } else {
        await api.createJournalEntry(formData)
      }

      // Reset form and reload
      setFormData({
        date: format(new Date(), 'yyyy-MM-dd'),
        title: '',
        content: '',
        tags: '',
      })
      setShowForm(false)
      setEditingEntry(null)
      loadEntries()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const handleEdit = (entry: JournalEntry) => {
    setEditingEntry(entry)
    setFormData({
      date: entry.date,
      title: entry.title,
      content: entry.content,
      tags: entry.tags || '',
    })
    setShowForm(true)
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Are you sure you want to delete this entry?')) return

    try {
      await api.deleteJournalEntry(id)
      loadEntries()
    } catch (err: any) {
      setError(err.message)
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingEntry(null)
    setFormData({
      date: format(new Date(), 'yyyy-MM-dd'),
      title: '',
      content: '',
      tags: '',
    })
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Trading Journal</h1>
          <p className="text-gray-600">
            Document your trading decisions and market observations
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="btn btn-primary"
        >
          {showForm ? 'Cancel' : '+ New Entry'}
        </button>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Entry Form */}
      {showForm && (
        <div className="card mb-6">
          <h2 className="text-xl font-semibold mb-4">
            {editingEntry ? 'Edit Entry' : 'New Journal Entry'}
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="label">Date</label>
                <input
                  type="date"
                  value={formData.date}
                  onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                  className="input"
                  required
                  disabled={!!editingEntry}
                />
              </div>
              <div>
                <label className="label">Tags (comma-separated)</label>
                <input
                  type="text"
                  value={formData.tags}
                  onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                  className="input"
                  placeholder="e.g., breakout, ES, profitable"
                />
              </div>
            </div>

            <div>
              <label className="label">Title</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="input"
                placeholder="Entry title"
                required
              />
            </div>

            <div>
              <label className="label">Content</label>
              <textarea
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="input"
                rows={6}
                placeholder="What happened today? What did you learn? What would you do differently?"
                required
              />
            </div>

            <div className="flex justify-end space-x-4">
              <button
                type="button"
                onClick={handleCancel}
                className="btn btn-secondary"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
              >
                {editingEntry ? 'Update Entry' : 'Save Entry'}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Entries List */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p className="mt-4 text-gray-600">Loading journal entries...</p>
        </div>
      ) : entries.length === 0 ? (
        <div className="card text-center py-12">
          <p className="text-gray-500 mb-4">No journal entries yet</p>
          <button
            onClick={() => setShowForm(true)}
            className="btn btn-primary"
          >
            Create Your First Entry
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          {entries.map(entry => (
            <div key={entry.id} className="card hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {entry.title}
                  </h3>
                  <p className="text-sm text-gray-500">
                    {format(new Date(entry.date), 'EEEE, MMMM dd, yyyy')}
                  </p>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(entry)}
                    className="text-primary-600 hover:text-primary-700 text-sm font-medium"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => handleDelete(entry.id)}
                    className="text-red-600 hover:text-red-700 text-sm font-medium"
                  >
                    Delete
                  </button>
                </div>
              </div>

              <div className="prose prose-sm max-w-none mb-3">
                <p className="text-gray-700 whitespace-pre-wrap">{entry.content}</p>
              </div>

              {entry.tags && (
                <div className="flex flex-wrap gap-2">
                  {entry.tags.split(',').map((tag, i) => (
                    <span
                      key={i}
                      className="px-2 py-1 bg-primary-100 text-primary-700 text-xs rounded"
                    >
                      {tag.trim()}
                    </span>
                  ))}
                </div>
              )}

              <div className="mt-3 pt-3 border-t border-gray-200 text-xs text-gray-500">
                Last updated: {format(new Date(entry.updated_at), 'MMM dd, yyyy HH:mm')}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

