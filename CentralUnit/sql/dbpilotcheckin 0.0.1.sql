
--
-- Datenbank: `dbpilotcheckin`
--

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `tattendance`
--

CREATE TABLE `tattendance` (
  `AID` bigint(20) UNSIGNED NOT NULL,
  `WID` int(11) NOT NULL,
  `PID` int(11) NOT NULL,
  `RID` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `tchannels`
--

CREATE TABLE `tchannels` (
  `CID` bigint(20) UNSIGNED NOT NULL,
  `channel_name` varchar(255) NOT NULL,
  `band` int(11) NOT NULL,
  `channel` int(11) NOT NULL,
  `slot` varchar(255) NOT NULL,
  `port` varchar(255) NOT NULL,
  `typ` varchar(255) NOT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `tpilots`
--

CREATE TABLE `tpilots` (
  `PID` bigint(20) UNSIGNED NOT NULL,
  `UID` varchar(255) NOT NULL,
  `callsign` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `traceoptions`
--

CREATE TABLE `traceoptions` (
  `ROID` bigint(20) UNSIGNED NOT NULL,
  `RID` int(11) NOT NULL,
  `option_name` varchar(255) NOT NULL,
  `option_value` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `traces`
--

CREATE TABLE `traces` (
  `RID` bigint(20) UNSIGNED NOT NULL,
  `race_date` date NOT NULL,
  `race_name` varchar(255) NOT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `trfid`
--

CREATE TABLE `trfid` (
  `RFIDID` bigint(20) UNSIGNED NOT NULL,
  `UID` varchar(255) NOT NULL,
  `PID` int(11) NOT NULL,
  `status` tinyint(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16;

-- --------------------------------------------------------

--
-- Tabellenstruktur für Tabelle `twaitlist`
--

CREATE TABLE `twaitlist` (
  `WID` bigint(20) UNSIGNED NOT NULL,
  `RID` int(11) NOT NULL,
  `AID` int(11) NOT NULL,
  `CID` int(11) NOT NULL,
  `wait_date` date NOT NULL,
  `wait_time` time NOT NULL,
  `update_date` date NOT NULL,
  `update_time` time NOT NULL,
  `status` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf16;

--
-- Indizes der exportierten Tabellen
--

--
-- Indizes für die Tabelle `tattendance`
--
ALTER TABLE `tattendance`
  ADD PRIMARY KEY (`AID`),
  ADD UNIQUE KEY `TID` (`AID`);

--
-- Indizes für die Tabelle `tchannels`
--
ALTER TABLE `tchannels`
  ADD PRIMARY KEY (`CID`),
  ADD UNIQUE KEY `CID` (`CID`);

--
-- Indizes für die Tabelle `tpilots`
--
ALTER TABLE `tpilots`
  ADD PRIMARY KEY (`PID`),
  ADD UNIQUE KEY `PID` (`PID`);

--
-- Indizes für die Tabelle `traceoptions`
--
ALTER TABLE `traceoptions`
  ADD PRIMARY KEY (`ROID`),
  ADD UNIQUE KEY `ROID` (`ROID`);

--
-- Indizes für die Tabelle `traces`
--
ALTER TABLE `traces`
  ADD PRIMARY KEY (`RID`),
  ADD UNIQUE KEY `RID` (`RID`);

--
-- Indizes für die Tabelle `trfid`
--
ALTER TABLE `trfid`
  ADD PRIMARY KEY (`RFIDID`),
  ADD UNIQUE KEY `RFIDID` (`RFIDID`);

--
-- Indizes für die Tabelle `twaitlist`
--
ALTER TABLE `twaitlist`
  ADD PRIMARY KEY (`WID`),
  ADD UNIQUE KEY `WID` (`WID`);

--
-- AUTO_INCREMENT für exportierte Tabellen
--

--
-- AUTO_INCREMENT für Tabelle `tattendance`
--
ALTER TABLE `tattendance`
  MODIFY `AID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT für Tabelle `tchannels`
--
ALTER TABLE `tchannels`
  MODIFY `CID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT für Tabelle `tpilots`
--
ALTER TABLE `tpilots`
  MODIFY `PID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT für Tabelle `traceoptions`
--
ALTER TABLE `traceoptions`
  MODIFY `ROID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT für Tabelle `traces`
--
ALTER TABLE `traces`
  MODIFY `RID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT für Tabelle `trfid`
--
ALTER TABLE `trfid`
  MODIFY `RFIDID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;
--
-- AUTO_INCREMENT für Tabelle `twaitlist`
--
ALTER TABLE `twaitlist`
  MODIFY `WID` bigint(20) UNSIGNED NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1;

