\version "2.13.31"

vlnone = \new Staff {
\relative c' {
  \set Staff.instrumentName = "violin-1"
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

g4\f( a b c)
d( e fis g)
a( b c d)
e( fis g a)
b4( c4 b2)

\bar "|."
}
}

vlntwo = \new Staff {
\relative c' {
  \set Staff.instrumentName = "violin-2"
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

r2 g4\f( a
b c) d( e
fis g) a( b
c d) e( fis
g4 a4) g2

\bar "|."
}
}

vlnthree = \new Staff {
\relative c' {
  \set Staff.instrumentName = "violin-3"
  \key g \major
  %\tempo 4 = 108
  \tempo 4 = 72

r1
g4\f( a
b c) d( e
fis g) a( b
c d) e( fis
g2)

\bar "|."
}
}

\score {
  <<
     \vlnone
     \vlntwo
     \vlnthree
  >>
  \layout{}
  \midi{}
}

