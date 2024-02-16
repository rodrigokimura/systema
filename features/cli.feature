Feature: CLI

  Scenario: Show version
    When I execute command in shell to show version
    Then shell should display current version
