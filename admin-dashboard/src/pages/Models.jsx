import React from 'react'
import { useNavigate } from 'react-router-dom'

const Models = () => {
  const navigate = useNavigate()

  React.useEffect(() => {
    // Redirect to brands page since models are managed there
    navigate('/brands')
  }, [navigate])

  return null
}

export default Models