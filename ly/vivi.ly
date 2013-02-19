\version "2.16.0"

\include "reduce-whitespace.ly"
\include "event-listener.ly"

st =
#(define-music-function
  (parser location text)
  (string?)
#{
  \override TextSpanner #'style = #'line
  \override TextSpanner #'(bound-details right padding) = #-1
  \override TextSpanner #'(bound-details left stencil-align-dir-y)
=
    #CENTER
  \override TextSpanner #'(bound-details right text) =
    \markup { \draw-line #'(0 . -1) }
  \override TextSpanner #'(bound-details left text) = $text
#})


