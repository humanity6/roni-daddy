import { useMemo } from 'react'

const SLOTS = [
  // Corners - strict corner positioning
  { top: '3%', left: '3%' },
  { top: '3%', right: '3%' },
  { bottom: '3%', left: '3%' },
  { bottom: '3%', right: '3%' },
  // Left and right edges only - no middle positions
  { left: '3%', top: '20%' },
  { left: '3%', top: '40%' },
  { left: '3%', bottom: '20%' },
  { right: '3%', top: '20%' },
  { right: '3%', top: '40%' },
  { right: '3%', bottom: '20%' },
  // Top and bottom edges only - closer to corners
  { top: '3%', left: '25%' },
  { top: '3%', right: '25%' },
  { bottom: '3%', left: '25%' },
  { bottom: '3%', right: '25%' },
]

// Helper function to check if two slots are too close to each other
const areSlotsTooClose = (slot1Idx, slot2Idx, slots) => {
  const slot1 = slots[slot1Idx]
  const slot2 = slots[slot2Idx]
  
  // Define adjacency rules to avoid clustering - more restrictive
  const adjacentPairs = [
    [0, 1], [0, 4], [0, 10], // top-left corner adjacencies
    [1, 7], [1, 11], // top-right corner adjacencies  
    [2, 3], [2, 6], [2, 12], // bottom-left corner adjacencies
    [3, 9], [3, 13], // bottom-right corner adjacencies
    [4, 5], [5, 6], [7, 8], [8, 9], // vertical edge adjacencies
    [10, 11], [12, 13] // horizontal edge adjacencies
  ]
  
  return adjacentPairs.some(([a, b]) => 
    (slot1Idx === a && slot2Idx === b) || (slot1Idx === b && slot2Idx === a)
  )
}

const PastelBlobs = () => {
  // A fixed set of blobs (colour, size and exact positioning) so that the
  // background now always matches the reference mock-up.  Feel free to tweak the
  // numbers to fine-tune the look, but avoid making them random – the designer
  // wants a deterministic backdrop across screens.

  const blobs = useMemo(
    () => [
      // Top-left – light blue
      {
        id: 1,
        color: '#D8ECF4',
        style: {
          top: '-40px',
          left: '-60px',
          width: '180px',
          height: '160px',
          borderRadius: '65% 35% 70% 30% / 60% 55% 45% 55%',
        },
      },
      // Top-right – soft pink
      {
        id: 2,
        color: '#F8D9DE',
        style: {
          top: '-30px',
          right: '-40px',
          width: '160px',
          height: '190px',
          borderRadius: '40% 60% 55% 45% / 50% 60% 40% 50%',
        },
      },
      // Mid-right – light blue (slightly off-screen)
      {
        id: 3,
        color: '#D8ECF4',
        style: {
          top: '42%',
          right: '-90px',
          width: '180px',
          height: '180px',
          borderRadius: '30% 70% 65% 35% / 55% 45% 60% 40%',
        },
      },
      // Bottom-left – deeper pink
      {
        id: 4,
        color: '#F8D9DE',
        style: {
          bottom: '-40px',
          left: '-70px',
          width: '190px',
          height: '170px',
          borderRadius: '70% 30% 60% 40% / 65% 35% 55% 45%',
        },
      },
      // Bottom-right – pale green
      {
        id: 5,
        color: '#DDF4C8',
        style: {
          bottom: '-50px',
          right: '-60px',
          width: '220px',
          height: '210px',
          borderRadius: '55% 45% 50% 50% / 60% 50% 65% 35%',
        },
      },
    ],
    [],
  )

  return (
    <div className="pastel-blobs">
      {blobs.map((blob) => (
        <div
          key={blob.id}
          className="blob"
          style={{
            position: 'absolute',
            background: blob.color,
            borderRadius: blob.style.borderRadius,
            zIndex: -1,
            opacity: 0.8,
            width: blob.style.width,
            height: blob.style.height,
            top: blob.style.top,
            left: blob.style.left,
            right: blob.style.right,
            bottom: blob.style.bottom,
          }}
        />
      ))}
    </div>
  )
}

export default PastelBlobs 