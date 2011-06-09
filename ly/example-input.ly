\version "2.14.0"

violinone = \relative c' {
  \key d \major
  \tempo 4 = 96
  c'4
}

\score {
  <<
    \new Staff {
      \set Staff.instrumentName = "violin-1"
      \set Staff.midiInstrument = "violin"
      \violinone
    }
   >>
  \layout{}
  \midi{}
}

