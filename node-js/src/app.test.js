import { describe, it, expect } from 'vitest'
import { existsSync } from 'fs'

function isFileExists(filePath) {
  return existsSync(filePath)
}

describe('isFileExists', () => {
  it('returns false for a path that does not exist', () => {
    expect(isFileExists('/tmp/__vitest_nonexistent__')).toBe(false)
  })

  it('returns true for a path that exists', () => {
    expect(isFileExists('/tmp')).toBe(true)
  })
})
