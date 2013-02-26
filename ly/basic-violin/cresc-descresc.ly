\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "violin-1"
\relative c' {
  \key g \major
  %\tempo 4 = 108
  %\tempo 4 = 72
  \tempo 4 = 120

    \numericTimeSignature
    \key g \major
    g1\pp\< ~ g1\ff\>
    d'1\pp\< ~ d1\ff\>
    a'1\pp\< ~ a1\ff\>
    e'1\pp\< ~ e2...\ff\> ~ e16\pp

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

