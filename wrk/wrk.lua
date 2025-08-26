wrk.headers["Accept"   ] = "application/json"
wrk.headers["Content-Type"] = "application/json"


local BASE = "http://localhost:8080"

local paths = {
    dashboard = "/api/dashboard",
    simulate = "/api/simulate",
    station = "/api/station",
}

local station_ids = { "GS-001", "GS-002", "GS-003", "GS-004", "GS-005",
                      "GS-006", "GS-007", "GS-008", "GS-009", "GS-010" }

loca mix = {
    {"dashboard", 5}
    {"simulate", 1},
    {"station", 7}
}


local function choose(weighted)
    local sum, i = 0, 1
    for _, p in ipairs(weighted) do sum = sum + p[2] end
    local r = math.random() * sum
    local acc = 0
    for _, p in ipairs(weighted) do
      acc = acc + p[2]
      if r <= acc then return p[1] end
    end
    return weighted[#weighted][1]
  end

  local function rand_station()
    return station_ids[math.random(#station_ids)]
  end
  
  request = function()
    local which = choose(mix)
  
    if which == "dashboard" then
      wrk.method = "GET"
      return wrk.format(nil, BASE .. paths.dashboard)
  
    elseif which == "station" then
      wrk.method = "GET"
      local sid = rand_station()
      return wrk.format(nil, BASE .. paths.station .. sid)
  
    elseif which == "simulate" then
      wrk.method = "GET"
      return wrk.format(nil, BASE .. paths.simulate)
    end
  
    -- Fallback
    wrk.method = "GET"
    return wrk.format(nil, BASE .. paths.dashboard)
  end