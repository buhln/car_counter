% Code to interpret the counted car numbers of car counter on Thingspeak.com
% Nico Buhl, October 2021

% channel ID to read data from:
readChannelID = 0815;
% Field IDs to read data from:
% Read the points of the last day (6 p/h)
anz_read_points = 24*120;

% Channel Read API Key
% If your channel is private, then enter the read API
% Key between the '' below:
readAPIKey = 'HERE_YOUR_CHANNEL_READ_KEY';

% time vector for every hour
timeHr = hours(1:25);
% Vector for hourly values
cars_north_Hr = int16.empty(length(timeHr), 0);
cars_south_Hr = int16.empty(length(timeHr), 0);
cars_Hr = zeros(length(timeHr), 3);

last24h = [datetime('now')-hours(25) datetime('now')];
% Read of all data for last 24h in timetable format
data_24h = thingSpeakRead(readChannelID,'Fields',[1,2],'dateRange', last24h,'ReadKey',readAPIKey,'OutputFormat','TimeTable');

% Split data hourly for the last 24h
for n=1:25,
    if n==1,
        % Ongoing hour is proportionate used
        TR_start = datetime('now') - minutes(minute(datetime('now'))) - seconds(round(second(datetime('now'))));
        TR_end = datetime('now') - hours(n-1);
    else
        % All other hours are used completly
        TR_start = datetime('now') - minutes(minute(datetime('now'))) - seconds(round(second(datetime('now')))) - hours(n-1);
        TR_end = datetime('now') - minutes(minute(datetime('now'))) - seconds(round(second(datetime('now')))) - hours(n-2);
    end
    TR = timerange(TR_start,TR_end);
    data_lasthour = data_24h(TR,:);
    cars_north_Hr(n) = sum(data_lasthour.cars_north);
    cars_south_Hr(n) = sum(data_lasthour.cars_south);
end

cars_north_Hr = flip(cars_north_Hr);
cars_south_Hr = flip(cars_south_Hr);
cars_total_Hr = cars_north_Hr + cars_south_Hr;

for n=1:length(timeHr),
    cars_Hr(n,:) = [cars_north_Hr(n), cars_south_Hr(n), cars_total_Hr(n)];
end

% Create x-values with datetime object
x_time_24hr = (datetime('now','TimeZone','+01:00')-hours(24)):hours(1):datetime('now','TimeZone','+01:00');

%% Visualize data %%
bar(x_time_24hr,[cars_Hr(:,1), cars_Hr(:,2), cars_Hr(:,3)]);

tend = datetime('now','TimeZone','+01:00')+hours(1);
tstart = datetime('now','TimeZone','+01:00')-hours(24);

ylabel('Number of motor vehicle on B271');
xlabel('Time (Hour)');
xticks(tstart:hours(1):tend);
datetick('x', 'HH', 'keepticks', 'keeplimits');

grid on;
legend('Cars to north', 'Cars to south', 'Cars total');
legend('Location','southwest');