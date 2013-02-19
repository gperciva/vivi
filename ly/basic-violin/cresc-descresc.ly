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
    g1\p\< ~ g1\f\>
    d'1\p\< ~ d1\f\>
    a'1\p\< ~ a1\f\>
    e'1\p\< ~ e2...\f\> ~ e16\p

\bar "|."
}
}

\score {
  << \vlnone >>
  \layout{}
  \midi{}
}

