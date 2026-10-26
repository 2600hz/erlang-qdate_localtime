%% Date-sensitive corrections to the legacy recurring-rule snapshot.
%% The original snapshot remains the source for all earlier timestamps.
-module(localtime_tzdata).

-include("tz_database.hrl").

-export([lookup/3, dst/2]).

%% IANA tzdata 2026e models these Canadian changes at 02:00 local daylight
%% time on 2026-11-01. The UTC offset does not change at that instant; only
%% the abbreviation and DST classification change. See:
%% https://data.iana.org/time-zones/tzdb-2026e/northamerica
%% https://data.iana.org/time-zones/tzdb-2026e/backward
-define(CANADA_LOCAL_TRANSITION, {{2026,11,1},{2,0,0}}).
-define(CANADA_CANCELLED_OVERLAP, {{2026,11,1},{1,0,0}}).

%% Timezone has already been normalized by localtime:get_timezone/1.
%% utc_to_local supplies a UTC datetime; the other entry points supply local
%% wall time. Comparing the correct basis matters near the transition.
lookup(Timezone, DateTime, Basis) ->
    Rule = lists:keyfind(Timezone, 1, ?tz_database),
    case canada_rule(Timezone) of
        false -> Rule;
        {Shift, Name} ->
            From = transition_datetime(Shift, Basis),
            case DateTime >= From of
                true -> {Timezone, Name, undef, Shift, 0, undef, {0,0}, undef, {0,0}};
                false -> Rule
            end
    end.

%% Used by localtime_dst, including callers that pass a legacy rule tuple
%% directly. The last fall-back overlap is cancelled: 01:00-01:59 occurs
%% once, in daylight time, before the permanent standard-time era starts.
dst(LocalDateTime, Timezone) ->
    case canada_rule(Timezone) of
        false -> legacy;
        _ when LocalDateTime >= ?CANADA_LOCAL_TRANSITION -> is_not_in_dst;
        _ when LocalDateTime >= ?CANADA_CANCELLED_OVERLAP -> is_in_dst;
        _ -> legacy
    end.

transition_datetime(Shift, utc) ->
    localtime:adjust_datetime(?CANADA_LOCAL_TRANSITION, -Shift);
transition_datetime(_Shift, local) ->
    ?CANADA_LOCAL_TRANSITION.

canada_rule("America/Vancouver") -> {-420, {"MST","MST"}};
canada_rule("Canada/Pacific") -> canada_rule("America/Vancouver");
canada_rule("America/Edmonton") -> {-360, {"CST","CST"}};
canada_rule("Canada/Mountain") -> canada_rule("America/Edmonton");
canada_rule("America/Yellowknife") -> canada_rule("America/Edmonton");
canada_rule("America/Inuvik") -> {-360, {"CST","CST"}};
canada_rule("America/Winnipeg") -> {-300, {"EST","EST"}};
canada_rule("Canada/Central") -> canada_rule("America/Winnipeg");
canada_rule("America/Rainy_River") -> canada_rule("America/Winnipeg");
canada_rule(_) -> false.
