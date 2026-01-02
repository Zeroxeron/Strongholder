<div align="center"><center>
<img width="128" height="128" alt="icon" src="https://github.com/user-attachments/assets/2c107b82-0a4d-47aa-9c3e-1ad64a4101ba" />

# Minecraft Strongholder

## Simple and handy stronghold position calculator with a map!

Features real-time F3+C clipboard grab, direction lines, Stronghold pos, Nether coords, interactive XZ graph mapping, zoom/pan controls, and image export and extensively explained config. 

Perfect for speedruns, survival worlds, and finding End portals with high accuracy.

Check FAQ for specifics

## Demo:

<div align="left">
      <a href="https://www.youtube.com/watch?v=Ka5fh-_XXag">
         <img src="https://img.youtube.com/vi/Ka5fh-_XXag/0.jpg" style="width:100%;">
      </a>
</div>

</center></div>

Minecraft stronghold finding is essentially geometric triangulation! 

When you throw an Ender Eye, it points toward the nearest stronghold. By throwing from two different locations and recording where they point, you create two directional lines. The intersection point of these lines reveals the stronghold's exact coordinates!

![demo2](https://github.com/user-attachments/assets/5ad3c44c-ed0e-4173-a6df-1b6c0780d430)

## Real-time processing

Works in the background / second monitor.

Auto-grabs your F3+C clipboard!

![rt](https://github.com/user-attachments/assets/5777e82a-39b9-437f-bd3c-2691a6ed8e5d)

## Interface

-Shows the stronghold position.

-Shows nether portal position (in brackets: [x z])

-Shows average target stronghold distance from your trow line.

-Allows you to navigate the graph and check the precision

-Allows you to export (save) the graph

<img width="640" height="480" alt="Minecraft_Strongholder_v1 1" src="https://github.com/user-attachments/assets/ad8f7eb0-0e90-4b37-ad14-836bf775d146" />

<img width="640" height="480" alt="Minecraft_Strongholder_v1 12" src="https://github.com/user-attachments/assets/21b62bdd-1865-436c-9dfa-bb8d03660a20" />

<img width="638" height="551" alt="Minecraft_Strongholder_v1 3" src="https://github.com/user-attachments/assets/513546c3-4010-47c3-847a-131c55b7d9a1" />

## FAQ:

### Q: Can it locate stronghold with just one eye throw?
A: Yes, it can. However, this requires high precision and special config. With the default config its no near to be consistent for accurate 1-throw measurements. 

I dont have a reliable config right now, so the best way is to test angle offset by your own (start with 0.0). 

Share your config [-> here <-]([https://docs.google.com/forms/d/e/1FAIpQLSfJ6kmW3wh3500wLIiML7Rh5uka3LB_FR7qOkK3164aDFVgEw/viewform?usp=dialog). 

Check others presets [-> here <-](https://docs.google.com/spreadsheets/d/1IWk2itZGarPUd6qIu9gpQD8-IB-BSi4TRezSc3XGLms/edit?resourcekey=&gid=1024968442#gid=1024968442).

### Q: Why is it 50mb?
A: My PyInstaller grabbed some chunky libs there, such as pandas and PyQt5. You can try building it by yourself with any another method.

### Q: Is it better than NinjaBrain's bot?
A: You should test it yourself!

### Q: Does it counts as cheating?
A: No, unless specified in the server/match/tournament rules. MCSR mentions other calculators in their tool list.

### Q: Can it do 2nd,3rd,4th ring?
A: Yes, it can. Change the config file (generates after the launch).

### Q: I found a bug!
A: Tell about it more [-> here <-](https://github.com/Zeroxeron/Strongholder/issues)

### Q: I want to contribute, how can I do that?
A: Try making a pull req [-> here <-](https://github.com/Zeroxeron/Strongholder/pulls)

### Q: Donations?
A: No, thanks.
