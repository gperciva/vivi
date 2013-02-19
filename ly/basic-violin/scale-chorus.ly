\version "2.13.31"

\include "../event-listener.ly"
\include "../reduce-whitespace.ly"

vlnone = \new Staff {
  \set Staff.instrumentName = "violin-1"
\relative c' {
  \key g \major
  \tempo 4 = 120

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlntwo = \new Staff {
  \set Staff.instrumentName = "violin-2"
\relative c' {
  \key g \major
  \tempo 4 = 120

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlnthree = \new Staff {
  \set Staff.instrumentName = "violin-3"
\relative c' {
  \key g \major
  \tempo 4 = 120

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlnfour = \new Staff {
  \set Staff.instrumentName = "violin-4"
\relative c' {
  \key g \major
  \tempo 4 = 120

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

vlnfive = \new Staff {
  \set Staff.instrumentName = "violin-5"
\relative c' {
  \key g \major
  \tempo 4 = 120

g4\mf a b c
d e fis g
a b c d
e fis g a
b a g2

\bar "|."
}
}

\score {
  <<
    \vlnone
    \vlntwo
    \vlnthree
    \vlnfour
    \vlnfive
  >>
  \layout{}
  \midi{}
}

