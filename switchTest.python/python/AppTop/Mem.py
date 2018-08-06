import pyrogue as pr

class Mem(pr.Device):
    def __init__(   self,
            name        = "Memory",
            nelms       = 0x1000,
            mode        = "RO",
            description = "Generic Memory",
            hidden      = True,
            **kwargs):
        super().__init__(name=name, description=description, hidden=hidden, **kwargs)

        self.nelms = nelms

        for i in range(nelms):
            # Cryo channel ETA
            self.add(pr.RemoteVariable(
                name         = f'Mem[{i}]',
                hidden       = True,
                description  = "ETA mag Fix_16_10",
                offset       =  0x000000 + i*4,
                bitSize      =  32,
                bitOffset    =  0,
                base         = pr.UInt,
                mode         = mode,
            ))

        @self.command()
        def read():
            with self.root.updateGroups():
                for i in range(self.nelms):
                    self.node(f'Mem[{i}]').get()
