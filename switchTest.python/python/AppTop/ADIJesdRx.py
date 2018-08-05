#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue JESD RX Module
#-----------------------------------------------------------------------------
# File       : ADIJesdRx.py
# Created    : 2017-04-12
#-----------------------------------------------------------------------------
# Description:
# PyRogue JESD RX Module
#-----------------------------------------------------------------------------
# This file is part of the rogue software platform. It is subject to
# the license terms in the LICENSE.txt file found in the top-level directory
# of this distribution and at:
#    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html.
# No part of the rogue software platform, including this file, may be
# copied, modified, propagated, or distributed except according to the terms
# contained in the LICENSE.txt file.
#-----------------------------------------------------------------------------

import pyrogue as pr

class ADIJesdRx(pr.Device):
    def __init__(   self,       
            name        = "JesdRx",
            description = "JESD RX Module",
            numRxLanes  =  10,
            instantiate =  True,
            debug	    =  False,
            **kwargs):
        super().__init__(name=name, description=description, **kwargs) 

        ##############################
        # Variables
        ##############################

        if (instantiate):
            self.add(pr.RemoteVariable(    
                name         = "Version",
                description  = "Version",
                offset       =  0x00,
                bitSize      =  32,
                bitOffset    =  0x00,
                base         = pr.UInt,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "Peripheral_ID",
                description  = "Value of the ID configuration parameter",
                offset       =  0x04,
                bitSize      =  32,
                bitOffset    =  0x00,
                base         = pr.UInt,
                mode         = "RO",
            ))
                            
            self.add(pr.RemoteVariable(    
                name         = "Scratch",
                description  = "Scratch register",
                offset       =  0x08,
                bitSize      =  32,
                bitOffset    =  0,
                base         = pr.UInt,
                mode         = "RW",
            ))                              

            self.add(pr.RemoteVariable(    
                name         = "Identification",
                description  = "Peripheral identification",
                offset       =  0x0C,
                bitSize      =  32,
                bitOffset    =  0x00,
                base         = pr.UInt,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SYNTH_NUM_LANES",
                description  = "Number of supported lanes",
                offset       =  0x10,
                bitSize      =  32,
                bitOffset    =  0x00,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SYNTH_DATA_PATH_WIDTH",
                description  = "Internal data path width in octets",
                offset       =  0x14,
                bitSize      =  32,
                bitOffset    =  0x00,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SYNTH_ELASTIC_BUFFER_SIZE",
                description  = "Elastic buffer size in octets",
                offset       =  0x18,
                bitSize      =  32,
                bitOffset    =  0x00,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "IRQ_ENABLE",
                description  = "Interrupt enable",
                offset       =  0x80,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "IRQ_PENDING",
                description  = "Pending and enabled interrupts, write to clear",
                offset       =  0x84,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "IRQ_SOURCE",
                description  = "Pending interrupts, write to clear",
                offset       =  0x88,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "LINK_DISABLE",
                description  = "Disable link",
                offset       =  0xC0,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "LINK_STATE",
                description  = "Link enabled",
                offset       =  0xC4,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "LINK_STATE_EXT_RESET",
                description  = "",
                offset       =  0xC4,
                bitSize      =  1,
                bitOffset    =  0x01,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "LINK_CLK_FREQ",
                description  = "Ratio of device_clk to s_axi_clk, UFix16_16",
                offset       =  0xC8,
                bitSize      =  16,
                bitOffset    =  0x00,
                mode         = "RO",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SYSREF_CONF",
                description  = "Enable/disable SYSREF handling",
                offset       =  0x100,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SYSREF_LMFC_OFFSET",
                description  = "Offset between SYSREF event and internal LMFC event in octets",
                offset       =  0x104,
                bitSize      =  10,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SYSREF_DETECTED",
                description  = "SYSREF event detected, write to clear",
                offset       =  0x108,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SYSREF_ALIGNMENT_ERROR",
                description  = "Exteranl SYSREF event unaligned to previously observed event, write to clear",
                offset       =  0x108,
                bitSize      =  1,
                bitOffset    =  0x01,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "LANE_DISABLE",
                description  = "Enable/Disable the n-th lane (0 = enabled, 1 = disabled)",
                offset       =  0x200,
                bitSize      =  10,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "OCTETS_PER_MULTIFRAME",
                description  = "Number of octets per multiframe",
                offset       =  0x210,
                bitSize      =  8,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "OCTETS_PER_FRAME",
                description  = "Number of octets per frame",
                offset       =  0x210,
                bitSize      =  3,
                bitOffset    =  16,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "SCRAMBLER_DISABLE",
                description  = "Disable scrambler",
                offset       =  0x214,
                bitSize      =  1,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "CHAR_REPLACEMENT_DISABLE",
                description  = "Disable data alignment character replacement",
                offset       =  0x214,
                bitSize      =  1,
                bitOffset    =  0x01,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "BUFFER_DELAY",
                description  = "Buffer release opportunity offset from LMFC",
                offset       =  0x240,
                bitSize      =  12,
                bitOffset    =  0x00,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "BUFFER_EARLY_RELEASE",
                description  = "Elastic buffer release point",
                offset       =  0x240,
                bitSize      =  1,
                bitOffset    =  16,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "RESET_COUNTER",
                description  = "Reset error counter",
                offset       =  0x244,
                bitSize      =  1,
                bitOffset    =  0,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "MASK_DISPERR",
                description  = "If set disparity errors are not counted",
                offset       =  0x244,
                bitSize      =  1,
                bitOffset    =  8,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "MASK_NOTINTABLE",
                description  = "If set not in table errors are not counted",
                offset       =  0x244,
                bitSize      =  1,
                bitOffset    =  9,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "MASK_UNEXPECTEDK",
                description  = "If set unexpected k errors are not counted",
                offset       =  0x244,
                bitSize      =  1,
                bitOffset    =  10,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(    
                name         = "LINK_STATUS_STATE",
                description  = "State of link state machine (0=RESET, 1=WAIT_FOR_PHY, 2=CGS, 3=SYNCHRONIZED)",
                offset       =  0x280,
                bitSize      =  2,
                bitOffset    =  0x00,
                mode         = "RO",
            ))
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_CGS_STATE[%d]'%i),
                    description  = "State of the lane code group synchronization (0=INIT, 1=CHECK, 2=DATA)",
                    offset       =  0x300 + 0x20*i,
                    bitSize      =  2,
                    bitOffset    =  0x00,
                    mode         = "RO",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_IFS_READY[%d]'%i),
                    description  = "Frame synchronization state",
                    offset       =  0x300 + 0x20*i,
                    bitSize      =  1,
                    bitOffset    =  4,
                    mode         = "RO",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_ILAS_READY[%d]'%i),
                    description  = "ILAS configuration data received",
                    offset       =  0x300 + 0x20*i,
                    bitSize      =  1,
                    bitOffset    =  5,
                    mode         = "RO",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_LATENCY[%d]'%i),
                    description  = "Lane latency in octets",
                    offset       =  0x304 + 0x20*i,
                    bitSize      =  14,
                    bitOffset    =  0,
                    mode         = "RO",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_ERRORS[%d]'%i),
                    description  = "Total errors for this lane.  It must always be manually reset",
                    offset       =  0x308 + 0x20*i,
                    bitSize      =  32,
                    bitOffset    =  0,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_DID[%d]'%i),
                    description  = "Device ID field of the ILAS config sequence",
                    offset       =  0x310 + 0x20*i,
                    bitSize      =  8,
                    bitOffset    =  16,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_BID[%d]'%i),
                    description  = "Bank ID field of the ILAS config sequence",
                    offset       =  0x310 + 0x20*i,
                    bitSize      =  4,
                    bitOffset    =  24,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_LID[%d]'%i),
                    description  = "Lane ID field of the ILAS config sequence",
                    offset       =  0x314 + 0x20*i,
                    bitSize      =  5,
                    bitOffset    =  0,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_L[%d]'%i),
                    description  = "Number of lanes field in the ILAS config sequence",
                    offset       =  0x314 + 0x20*i,
                    bitSize      =  5,
                    bitOffset    =  8,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_SCR[%d]'%i),
                    description  = "Scrambling enabled field of the ILAS config sequence",
                    offset       =  0x314 + 0x20*i,
                    bitSize      =  1,
                    bitOffset    =  15,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_F[%d]'%i),
                    description  = "Octets per frame field of the ILAS config sequence",
                    offset       =  0x314 + 0x20*i,
                    bitSize      =  8,
                    bitOffset    =  16,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_K[%d]'%i),
                    description  = "Frames per multiframe field of the ILAS config sequence",
                    offset       =  0x314 + 0x20*i,
                    bitSize      =  5,
                    bitOffset    =  24,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_M[%d]'%i),
                    description  = "Number of converters field of the ILAS config sequence",
                    offset       =  0x318 + 0x20*i,
                    bitSize      =  8,
                    bitOffset    =  0,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_N[%d]'%i),
                    description  = "Converter resolution field of the ILAS config sequence",
                    offset       =  0x318 + 0x20*i,
                    bitSize      =  5,
                    bitOffset    =  8,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_CS[%d]'%i),
                    description  = "Control bits per sample field of the ILAS config sequence",
                    offset       =  0x318 + 0x20*i,
                    bitSize      =  2,
                    bitOffset    =  14,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_NP[%d]'%i),
                    description  = "Total number of bits per sample field of the ILAS config sequence",
                    offset       =  0x318 + 0x20*i,
                    bitSize      =  5,
                    bitOffset    =  16,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_SUBCLASSV[%d]'%i),
                    description  = "Subclass field of the ILAS config sequence",
                    offset       =  0x318 + 0x20*i,
                    bitSize      =  3,
                    bitOffset    =  21,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_S[%d]'%i),
                    description  = "Samples per frame field of the ILAS config sequence",
                    offset       =  0x318 + 0x20*i,
                    bitSize      =  5,
                    bitOffset    =  24,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_JESDV[%d]'%i),
                    description  = "JESD204 version field of the ILAS config sequence",
                    offset       =  0x318 + 0x20*i,
                    bitSize      =  3,
                    bitOffset    =  29,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_CF[%d]'%i),
                    description  = "Control words per frame field of the ILAS config sequence",
                    offset       =  0x31C + 0x20*i,
                    bitSize      =  5,
                    bitOffset    =  0,
                    mode         = "RO",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_HD[%d]'%i),
                    description  = "High density field of the ILAS config sequence",
                    offset       =  0x31C + 0x20*i,
                    bitSize      =  1,
                    bitOffset    =  7,
                    mode         = "RW",
                ))
    
            for i in range(0, 10):
                self.add(pr.RemoteVariable(    
                    name         = ('LANE_FCHK[%d]'%i),
                    description  = "Checksum field of the ILAS config sequence",
                    offset       =  0x31C + 0x20*i,
                    bitSize      =  7,
                    bitOffset    =  24,
                    mode         = "RW",
                ))
           
            ##############################
            # Commands
            ##############################
            
            @self.command(name="CmdClearErrors", description="Clear the status valid counter of RX lanes.",)
            def CmdClearErrors():    
                self.IRQ_PENDING.set(0)
                self.IRQ_SOURCE.set(0)
                self.SYSREF_ALIGNMENT_ERROR.set(0)

            @self.command(name="CmdResetGTs", description="Toggle the reset of all RX MGTs",)
            def CmdResetGTs(): 
                #self.ResetGTs.set(1)
                #self.ResetGTs.set(0)                    
                pass 
