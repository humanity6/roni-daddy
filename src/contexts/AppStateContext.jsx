import { createContext, useContext, useReducer, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'

const AppStateContext = createContext()

// Initial state
const initialState = {
  // QR Session
  sessionId: null,
  qrSession: false,
  
  // Vending Machine Session
  vendingMachineSession: {
    isVendingMachine: false,
    machineId: null,
    sessionId: null,
    location: null,
    machineInfo: null,
    sessionStatus: null,
    expiresAt: null
  },
  
  // User selections
  brand: null,
  model: null,
  color: null,
  
  // Images and design
  uploadedImages: [],
  template: null,
  
  // Text customization (if applicable)
  customText: '',
  selectedFont: null,
  textColor: null,
  
  // AI Credits
  aiCredits: 4,
  
  // Order flow
  designComplete: false,
  orderNumber: null,
  queuePosition: null,
  orderStatus: 'designing', // designing, payment, queue, printing, completed
  
  // Error handling
  error: null,
  loading: false
}

// Action types
const ACTIONS = {
  SET_QR_SESSION: 'SET_QR_SESSION',
  SET_PHONE_SELECTION: 'SET_PHONE_SELECTION',
  SET_TEMPLATE: 'SET_TEMPLATE',
  ADD_IMAGE: 'ADD_IMAGE',
  REMOVE_IMAGE: 'REMOVE_IMAGE',
  SET_CUSTOM_TEXT: 'SET_CUSTOM_TEXT',
  SET_FONT: 'SET_FONT',
  SET_TEXT_COLOR: 'SET_TEXT_COLOR',
  SET_AI_CREDITS: 'SET_AI_CREDITS',
  DEDUCT_AI_CREDIT: 'DEDUCT_AI_CREDIT',
  SET_DESIGN_COMPLETE: 'SET_DESIGN_COMPLETE',
  SET_ORDER_STATUS: 'SET_ORDER_STATUS',
  SET_ORDER_NUMBER: 'SET_ORDER_NUMBER',
  SET_QUEUE_POSITION: 'SET_QUEUE_POSITION',
  SET_ERROR: 'SET_ERROR',
  SET_LOADING: 'SET_LOADING',
  RESET_STATE: 'RESET_STATE',
  SET_VENDING_MACHINE_SESSION: 'SET_VENDING_MACHINE_SESSION',
  UPDATE_VENDING_SESSION_STATUS: 'UPDATE_VENDING_SESSION_STATUS'
}

// Reducer
const appStateReducer = (state, action) => {
  switch (action.type) {
    case ACTIONS.SET_QR_SESSION:
      return {
        ...state,
        sessionId: action.payload.sessionId,
        qrSession: action.payload.qrSession
      }
    
    case ACTIONS.SET_PHONE_SELECTION:
      return {
        ...state,
        brand: action.payload.brand,
        model: action.payload.model,
        color: action.payload.color
      }
    
    case ACTIONS.SET_TEMPLATE:
      return {
        ...state,
        template: action.payload
      }
    
    case ACTIONS.ADD_IMAGE:
      return {
        ...state,
        uploadedImages: [...state.uploadedImages, action.payload]
      }
    
    case ACTIONS.REMOVE_IMAGE:
      return {
        ...state,
        uploadedImages: state.uploadedImages.filter((_, index) => index !== action.payload)
      }
    
    case ACTIONS.SET_CUSTOM_TEXT:
      return {
        ...state,
        customText: action.payload
      }
    
    case ACTIONS.SET_FONT:
      return {
        ...state,
        selectedFont: action.payload
      }
    
    case ACTIONS.SET_TEXT_COLOR:
      return {
        ...state,
        textColor: action.payload
      }
    
    case ACTIONS.SET_AI_CREDITS:
      return {
        ...state,
        aiCredits: action.payload
      }
    
    case ACTIONS.DEDUCT_AI_CREDIT:
      return {
        ...state,
        aiCredits: Math.max(0, state.aiCredits - 1)
      }
    
    case ACTIONS.SET_DESIGN_COMPLETE:
      return {
        ...state,
        designComplete: action.payload
      }
    
    case ACTIONS.SET_ORDER_STATUS:
      return {
        ...state,
        orderStatus: action.payload
      }
    
    case ACTIONS.SET_ORDER_NUMBER:
      return {
        ...state,
        orderNumber: action.payload
      }
    
    case ACTIONS.SET_QUEUE_POSITION:
      return {
        ...state,
        queuePosition: action.payload
      }
    
    case ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload
      }
    
    case ACTIONS.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      }
    
    case ACTIONS.RESET_STATE:
      return {
        ...initialState,
        sessionId: state.sessionId,
        qrSession: state.qrSession,
        aiCredits: 4
      }
    
    case ACTIONS.SET_VENDING_MACHINE_SESSION:
      return {
        ...state,
        vendingMachineSession: {
          ...state.vendingMachineSession,
          ...action.payload
        }
      }
    
    case ACTIONS.UPDATE_VENDING_SESSION_STATUS:
      return {
        ...state,
        vendingMachineSession: {
          ...state.vendingMachineSession,
          sessionStatus: action.payload.status,
          ...action.payload
        }
      }
    
    case 'LOAD_STATE':
      return {
        ...action.payload,
        // Keep current QR session data and don't persist loading/error states
        sessionId: state.sessionId,
        qrSession: state.qrSession,
        loading: false,
        error: null
      }
    
    default:
      return state
  }
}

// Provider component
export const AppStateProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appStateReducer, initialState)
  const [searchParams] = useSearchParams()

  // Initialize QR session on mount
  useEffect(() => {
    const sessionId = searchParams.get('session')
    const qrSession = searchParams.has('qr')
    const machineId = searchParams.get('machine_id')
    const vendingSessionId = searchParams.get('session_id')
    const location = searchParams.get('location')
    
    if (sessionId || qrSession) {
      dispatch({
        type: ACTIONS.SET_QR_SESSION,
        payload: { sessionId, qrSession }
      })
    }
    
    // Handle vending machine QR parameters
    if (qrSession && machineId && vendingSessionId) {
      const vendingMachineData = {
        isVendingMachine: true,
        machineId,
        sessionId: vendingSessionId,
        location,
        sessionStatus: 'qr_scanned'
      }
      
      dispatch({
        type: ACTIONS.SET_VENDING_MACHINE_SESSION,
        payload: vendingMachineData
      })
      
      // Register user with vending machine session
      registerWithVendingMachine(vendingSessionId, machineId, location)
    }
  }, [searchParams])
  
  // Function to register user with vending machine session
  const registerWithVendingMachine = async (sessionId, machineId, location) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/session/${sessionId}/register-user`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          machine_id: machineId,
          session_id: sessionId,
          location,
          user_agent: navigator.userAgent,
          ip_address: null // Could be determined on backend
        })
      })
      
      if (response.ok) {
        const sessionData = await response.json()
        dispatch({
          type: ACTIONS.SET_VENDING_MACHINE_SESSION,
          payload: {
            ...sessionData.machine_info,
            sessionStatus: 'registered',
            expiresAt: sessionData.expires_at,
            userProgress: sessionData.user_progress
          }
        })
      }
    } catch (error) {
      console.error('Failed to register with vending machine session:', error)
      dispatch({
        type: ACTIONS.SET_ERROR,
        payload: 'Failed to connect to vending machine. Please try scanning the QR code again.'
      })
    }
  }

  // Persist state to localStorage
  useEffect(() => {
    const stateToSave = {
      ...state,
      // Don't persist loading states
      loading: false,
      error: null
    }
    localStorage.setItem('pimpMyCase_state', JSON.stringify(stateToSave))
  }, [state])

  // Load state from localStorage on mount
  useEffect(() => {
    const savedState = localStorage.getItem('pimpMyCase_state')
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState)
        // Merge with current state, keeping QR session params
        dispatch({
          type: 'LOAD_STATE',
          payload: {
            ...parsedState,
            sessionId: state.sessionId,
            qrSession: state.qrSession
          }
        })
      } catch (error) {
        console.error('Failed to load saved state:', error)
      }
    }
  }, [])

  // Action creators
  const actions = {
    setQrSession: (sessionId, qrSession) => dispatch({
      type: ACTIONS.SET_QR_SESSION,
      payload: { sessionId, qrSession }
    }),
    
    setPhoneSelection: (brand, model, color) => dispatch({
      type: ACTIONS.SET_PHONE_SELECTION,
      payload: { brand, model, color }
    }),
    
    setTemplate: (template) => dispatch({
      type: ACTIONS.SET_TEMPLATE,
      payload: template
    }),
    
    addImage: (image) => dispatch({
      type: ACTIONS.ADD_IMAGE,
      payload: image
    }),
    
    removeImage: (index) => dispatch({
      type: ACTIONS.REMOVE_IMAGE,
      payload: index
    }),
    
    setCustomText: (text) => dispatch({
      type: ACTIONS.SET_CUSTOM_TEXT,
      payload: text
    }),
    
    setFont: (font) => dispatch({
      type: ACTIONS.SET_FONT,
      payload: font
    }),
    
    setTextColor: (color) => dispatch({
      type: ACTIONS.SET_TEXT_COLOR,
      payload: color
    }),
    
    setAiCredits: (credits) => dispatch({
      type: ACTIONS.SET_AI_CREDITS,
      payload: credits
    }),
    
    deductAiCredit: () => dispatch({
      type: ACTIONS.DEDUCT_AI_CREDIT
    }),
    
    setDesignComplete: (complete) => dispatch({
      type: ACTIONS.SET_DESIGN_COMPLETE,
      payload: complete
    }),
    
    setOrderStatus: (status) => dispatch({
      type: ACTIONS.SET_ORDER_STATUS,
      payload: status
    }),
    
    setOrderNumber: (orderNumber) => dispatch({
      type: ACTIONS.SET_ORDER_NUMBER,
      payload: orderNumber
    }),
    
    setQueuePosition: (position) => dispatch({
      type: ACTIONS.SET_QUEUE_POSITION,
      payload: position
    }),
    
    setError: (error) => dispatch({
      type: ACTIONS.SET_ERROR,
      payload: error
    }),
    
    setLoading: (loading) => dispatch({
      type: ACTIONS.SET_LOADING,
      payload: loading
    }),
    
    resetState: () => dispatch({
      type: ACTIONS.RESET_STATE
    }),
    
    setVendingMachineSession: (sessionData) => dispatch({
      type: ACTIONS.SET_VENDING_MACHINE_SESSION,
      payload: sessionData
    }),
    
    updateVendingSessionStatus: (statusData) => dispatch({
      type: ACTIONS.UPDATE_VENDING_SESSION_STATUS,
      payload: statusData
    })
  }

  return (
    <AppStateContext.Provider value={{ state, actions }}>
      {children}
    </AppStateContext.Provider>
  )
}

// Custom hook
export const useAppState = () => {
  const context = useContext(AppStateContext)
  if (!context) {
    throw new Error('useAppState must be used within an AppStateProvider')
  }
  return context
}

export default AppStateContext 