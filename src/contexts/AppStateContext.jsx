import { createContext, useContext, useReducer, useEffect, useRef } from 'react'
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
    deviceId: null,  // Device ID for Chinese API stock/model queries
    sessionId: null,
    location: null,
    machineInfo: null,
    sessionStatus: null,
    expiresAt: null
  },
  
  // Brands Cache
  brandsCache: {
    brands: [],
    apiModels: {},
    deviceId: null, // Track which device_id the cache is for
    timestamp: null,
    loaded: false
  },
  
  // User selections
  brand: null,
  model: null,
  modelData: null,  // Complete model data including chinese_model_id, price, etc.
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
  UPDATE_VENDING_SESSION_STATUS: 'UPDATE_VENDING_SESSION_STATUS',
  SET_BRANDS_CACHE: 'SET_BRANDS_CACHE',
  CLEAR_BRANDS_CACHE: 'CLEAR_BRANDS_CACHE'
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
        modelData: action.payload.modelData,  // Store complete model data including chinese_model_id
        color: action.payload.modelData?.color || null  // Extract color from modelData if present
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
      {
        const merged = {
          ...state.vendingMachineSession,
          ...action.payload
        }
        // Auto-promote to vending if we have identifying info
        if (!merged.isVendingMachine && (merged.deviceId || merged.machineId || state.qrSession)) {
          merged.isVendingMachine = true
        }
        return {
          ...state,
          vendingMachineSession: merged
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
    
    case ACTIONS.SET_BRANDS_CACHE:
      return {
        ...state,
        brandsCache: {
          ...action.payload,
          timestamp: Date.now(),
          loaded: true
        }
      }
    
    case ACTIONS.CLEAR_BRANDS_CACHE:
      return {
        ...state,
        brandsCache: {
          brands: [],
          apiModels: {},
          deviceId: null,
          timestamp: null,
          loaded: false
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
  // Prevent duplicate registration attempts (e.g., double render / remount)
  const registrationAttemptedRef = useRef(false)
  const registrationRetryCountRef = useRef(0)

  // Initialize QR session on mount
  useEffect(() => {
    const sessionId = searchParams.get('session')
    const qrSession = searchParams.has('qr')
    const machineId = searchParams.get('machine_id')
    const deviceId = searchParams.get('device_id') || machineId  // device_id for Chinese API, fallback to machine_id
    const vendingSessionId = searchParams.get('session_id')
    const location = searchParams.get('location')
    const lang = searchParams.get('lang')
    
    console.log('QR Parameters extracted:', {
      sessionId, qrSession, machineId, deviceId, vendingSessionId, location, lang
    })
    
    if (sessionId || qrSession) {
      dispatch({
        type: ACTIONS.SET_QR_SESSION,
        payload: { sessionId, qrSession }
      })
    }
    
    // Handle vending machine QR parameters
    if (qrSession && (machineId || deviceId)) {
      const vendingMachineData = {
        isVendingMachine: true,
        machineId,
        deviceId,  // Store device_id separately for Chinese API
        sessionId: vendingSessionId,
        location,
        sessionStatus: 'qr_scanned'
      }
      
      console.log('Setting vending machine session:', vendingMachineData)
      
      dispatch({
        type: ACTIONS.SET_VENDING_MACHINE_SESSION,
        payload: vendingMachineData
      })

      // Persist deviceId immediately for refresh resilience
      if (deviceId) {
        localStorage.setItem('pimpMyCase_deviceId', deviceId)
      }
      
      // Register user with vending machine session if we have session ID
      if (vendingSessionId && machineId && !registrationAttemptedRef.current) {
        registrationAttemptedRef.current = true
        registerWithVendingMachine(vendingSessionId, machineId, location)
      }
    }
  }, [searchParams])

  // Recovery: if deviceId lost (e.g., after registration overwrite) but we have stored value, restore it
  useEffect(() => {
    if (!state.vendingMachineSession.deviceId) {
      const storedDeviceId = localStorage.getItem('pimpMyCase_deviceId')
      if (storedDeviceId) {
        dispatch({
          type: ACTIONS.SET_VENDING_MACHINE_SESSION,
          payload: {
            deviceId: storedDeviceId,
            isVendingMachine: state.vendingMachineSession.isVendingMachine || state.qrSession
          }
        })
      }
    }
  }, [state.vendingMachineSession.deviceId, state.qrSession])
  
  // Function to create a new vending machine session (for test scenarios)
  const createVendingMachineSession = async (machineId, location) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/create-session`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          machine_id: machineId,
          location: location || 'Test Location',
          session_timeout_minutes: 30,
          metadata: { source: 'test_qr_link' }
        }),
      })

      if (!response.ok) {
        throw new Error('Session creation failed')
      }

      const result = await response.json()
      return result.session_id
    } catch (error) {
      console.error('Vending machine session creation failed:', error)
      throw error
    }
  }

  // Function to register user with vending machine session
  const registerWithVendingMachine = async (sessionId, machineId, location) => {
    try {
      let finalSessionId = sessionId
      let response

      // First, try to register with the provided session ID
      try {
        response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/session/${sessionId}/register-user`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            machine_id: machineId,
            session_id: sessionId,
            location,
            user_agent: navigator.userAgent,
            ip_address: null
          })
        })

        // If registration successful, use original session
        if (response.ok) {
          finalSessionId = sessionId
        }
      } catch (registrationError) {
        console.log('Initial registration failed, will create new session')
        response = null
      }

      // If initial registration failed or returned 400/404, handle appropriately
      if (!response || !response.ok) {
        if (response?.status === 404) {
          // QR session expired - user needs to scan a fresh QR code
          console.error('QR session expired or not found. Machine needs to generate fresh QR code.')
          throw new Error('QR session expired. Please scan a fresh QR code from the vending machine.')
        }
        
        if (registrationRetryCountRef.current >= 3) {
          console.warn('Max vending registration retries reached; giving up.')
          throw new Error('Failed to create and register session')
        }
        console.log('Session registration failed, attempting to create new session (attempt', registrationRetryCountRef.current + 1, ')')

        try {
          finalSessionId = await createVendingMachineSession(machineId, location)
          registrationRetryCountRef.current += 1
          dispatch({
            type: ACTIONS.SET_VENDING_MACHINE_SESSION,
            payload: {
              ...state.vendingMachineSession,
              sessionId: finalSessionId,
              sessionStatus: 'session_created'
            }
          })
          // Register new session
          response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/vending/session/${finalSessionId}/register-user`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              machine_id: machineId,
              session_id: finalSessionId,
              location,
              user_agent: navigator.userAgent,
              ip_address: null
            })
          })
          if (!response.ok) {
            if (response.status === 429) {
              // Backoff retry
              const delay = 1000 * registrationRetryCountRef.current
              console.warn('Create/register rate limited (429). Retrying after', delay, 'ms')
              setTimeout(() => registerWithVendingMachine(sessionId, machineId, location), delay)
              return
            }
            throw new Error('Registration failed after new session creation')
          }
        } catch (createError) {
          console.error('Failed to create session:', createError)
          throw new Error('Failed to create and register session')
        }
      }
      
      if (response && response.ok) {
        const sessionData = await response.json()
        dispatch({
          type: ACTIONS.SET_VENDING_MACHINE_SESSION,
          payload: {
            // Preserve existing critical fields if machine_info doesn't provide them
            isVendingMachine: true,
            deviceId: state.vendingMachineSession.deviceId || sessionData.machine_info?.device_id || machineId,
            machineId: state.vendingMachineSession.machineId || sessionData.machine_info?.machine_id || machineId,
            location: state.vendingMachineSession.location || sessionData.machine_info?.location || '',
            sessionId: finalSessionId,
            sessionStatus: 'registered',
            expiresAt: sessionData.expires_at,
            userProgress: sessionData.user_progress,
            // Spread any additional machine info (non-destructive for already set keys)
            ...sessionData.machine_info
          }
        })
        // Re-persist deviceId
        if (state.vendingMachineSession.deviceId) {
          localStorage.setItem('pimpMyCase_deviceId', state.vendingMachineSession.deviceId)
        }
        console.log(`Successfully registered with session: ${finalSessionId}`)
      } else {
        throw new Error('Registration failed after session creation')
      }
    } catch (error) {
      console.error('Failed to register with vending machine session:', error)
      dispatch({
        type: ACTIONS.SET_ERROR,
        payload: 'Failed to connect to vending machine. Please try scanning the QR code again.'
      })
      // Mark registration failed but keep vending mode for device-specific flows
      dispatch({
        type: ACTIONS.SET_VENDING_MACHINE_SESSION,
        payload: {
          isVendingMachine: true,
          sessionStatus: 'registration_failed'
        }
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

  // Load state from localStorage on mount (but DO NOT override live QR session params if present in URL)
  useEffect(() => {
    const savedState = localStorage.getItem('pimpMyCase_state')
    if (savedState) {
      try {
        const parsedState = JSON.parse(savedState)
        const hasQrParams = searchParams.has('qr') && (searchParams.get('machine_id') || searchParams.get('device_id'))
        if (!hasQrParams) {
          dispatch({
            type: 'LOAD_STATE',
            payload: {
              ...parsedState,
              sessionId: state.sessionId,
              qrSession: state.qrSession
            }
          })
        } else {
          console.log('Skipping localStorage state hydrate to preserve live QR vending machine params')
        }
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
    
    setPhoneSelection: (brand, model, modelData) => dispatch({
      type: ACTIONS.SET_PHONE_SELECTION,
      payload: { brand, model, modelData }
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
    }),
    
    setBrandsCache: (brands, apiModels, deviceId) => dispatch({
      type: ACTIONS.SET_BRANDS_CACHE,
      payload: { brands, apiModels, deviceId }
    }),
    
    clearBrandsCache: () => dispatch({
      type: ACTIONS.CLEAR_BRANDS_CACHE
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