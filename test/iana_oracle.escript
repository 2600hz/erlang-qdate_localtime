#!/usr/bin/env escript
-mode(compile).

%% Vectors are generated independently by Python zoneinfo and IANA's zic.
main([Ebin, VectorsPath]) ->
    true = code:add_patha(Ebin),
    {ok, [Vectors]} = file:consult(VectorsPath),
    lists:foreach(fun check/1, Vectors),
    io:format("IANA oracle: ~p vectors passed (OTP ~s)~n",
              [length(Vectors), erlang:system_info(otp_release)]);
main(_) ->
    io:format(standard_error, "usage: iana_oracle.escript EBIN VECTORS.terms~n", []),
    halt(64).

check({Utc, Zone, Local, Name, Dst, Shift}) ->
    Expected = {Local, Utc, {Name, Name}, Dst, Shift},
    Actual = {localtime:utc_to_local(Utc, Zone),
              localtime:local_to_utc(Local, Zone),
              localtime:tz_name(Local, Zone),
              localtime_dst:check(Local, Zone),
              localtime:fmt_shift(localtime:tz_shift(Local, Zone))},
    case Actual of
        Expected -> ok;
        _ -> erlang:error({iana_mismatch, Zone, Utc, Expected, Actual})
    end.
