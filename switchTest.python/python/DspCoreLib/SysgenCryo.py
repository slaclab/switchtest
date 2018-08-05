#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : PyRogue AMC Carrier Cryo Demo Board Application
#-----------------------------------------------------------------------------
# File       : SysgenCryo.py
# Created    : 2017-04-03
#-----------------------------------------------------------------------------
# Description:
# PyRogue AMC Carrier Cryo Demo Board Application
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
import time
import math

class CryoChannel(pr.Device):
    def __init__(   self,
            name        = "Cryo frequency cord",
            description = "Note: This module is read-only with respect to sysgen",
            hidden      = True,
            index       = 0,
            parent      = None,
            **kwargs):
        super().__init__(name=name, description=description, hidden=hidden, **kwargs)

        freqSpanMHz = 9.6
        ##############################
        # Configuration registers (RO from Sysgen)
        ##############################
        i = index
        self.add(pr.LinkVariable(
            name         = "etaMagScaled",
            description  = "ETA mag scaled",
            dependencies = [parent.node(f'etaMag[{i}]')],
            linkedGet    = lambda var: var.dependencies[0].value()*2**-10,
            linkedSet    = lambda var, value, write: var.dependencies[0].set(round(value*2**10), write=write),
            typeStr      = "Float64",
        ))

        self.add(pr.LinkVariable(
            name         = "etaPhaseDegree",
            description  = "ETA phase degrees",
            dependencies = [parent.node(f'etaPhase[{i}]')],
            linkedGet    = lambda var: var.dependencies[0].value()*180*2**-15,
            linkedSet    = lambda var, value, write: var.dependencies[0].set(round(value*2**15./180), write=write),
            typeStr      = "Float64",
        ))

        # Cryo channel frequency word
        self.add(pr.LinkVariable(
            name         = "feedbackEnable",
            description  = "Enable feedback on this channel UFix_1_0",
            variable     = parent.node(f'feedbackEnable[{i}]'),
            typeStr      = "UInt1",
        ))

        self.add(pr.LinkVariable(
            name         = "amplitudeScale",
            description  = "Amplitdue scale UFix_4_0",
            variable     = parent.node(f'amplitudeScale[{i}]'),
            typeStr      = "UInt4",
        ))

        self.add(pr.LinkVariable(
            name         = "centerFrequencyMHz",
            description  = "Center frequency MHz",
            dependencies = [parent.node(f'centerFrequency[{i}]')],
            linkedGet    = lambda var: var.dependencies[0].value()*2**-24*freqSpanMHz,
            linkedSet    = lambda var, value, write: var.dependencies[0].set(round((value*2**24./freqSpanMHz)), write=write),
            typeStr      = "Float64",
        ))

        # Cryo channel readback loop filter output
        self.add(pr.LinkVariable(
            name         = "loopFilterOutput",
            description  = "Loop filter output UFix_24_24",
            variable     = parent.node(f'loopFilterOutput[{i}]'),
            typeStr      = "UInt24",
        ))

        self.add(pr.LinkVariable(
            name         = "amplitudeReadback",
            description  = "Loop filter output UFix_4_0",
            variable     = parent.node(f'amplitudeScale[{i}]'),
            typeStr      = "UInt4",
        ))

        self.add(pr.LinkVariable(
            name         = "frequencyErrorMHz",
            description  = "Frequency error Fix_24_23",
            mode         = "RO",
            dependencies = [parent.node(f'frequencyError[{i}]')],
            linkedGet    = lambda var, read: var.dependencies[0].get(read=read)*2**-23*freqSpanMHz,
            typeStr      = "Float64",
        ))

        self.add(pr.LinkVariable(
            name         = "frequencyError",
            hidden       = True,
            description  = "Frequency error Fix_24_23",
            mode         = "RO",
            variable     = parent.node(f'frequencyError[{i}]'),
            linkedGet    = lambda var, read: var.dependencies[0].get(read=read),
            typeStr      = "Float64",
        ))







class CryoChannels(pr.Device):
    def __init__(   self,
            name        = "CryoFrequencyBand",
            description = "Note: This module is read-only with respect to sysgen",
            hidden      = False,
            **kwargs):
        super().__init__(name=name, description=description, hidden=hidden, **kwargs)

#        ##############################
#        # Devices
#        ##############################
        for i in range(512):
            # Cryo channel ETA
            self.add(pr.RemoteVariable(
                name         = f'etaMag[{i}]',
                hidden       = True,
                description  = "ETA mag Fix_16_10",
                offset       =  0x0000 + i*4,
                bitSize      =  16,
                bitOffset    =  0,
                base         = pr.UInt,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(
                name         = f'etaPhase[{i}]',
                hidden       = True,
                description  = "ETA phase Fix_16_15",
                offset       =  0x0002 + i*4,
                bitSize      =  16,
                bitOffset    =  0,
                base         = pr.Int,
                mode         = "RW",
            ))

            # Cryo channel frequency word
            self.add(pr.RemoteVariable(
                name         = f'feedbackEnable[{i}]',
                hidden       = True,
                description  = "Enable feedback on this channel UFix_1_0",
                offset       =  0x0800 + i*4,
                bitSize      =  1,
                bitOffset    =  31,
                base         = pr.UInt,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(
                name         = f'amplitudeScale[{i}]',
                hidden       = True,
                description  = "Amplitdue scale UFix_4_0",
                offset       =  0x0800 + i*4,
                bitSize      =  4,
                bitOffset    =  24,
                base         = pr.UInt,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(
                name         = f'centerFrequency[{i}]',
                hidden       = True,
                description  = "Center frequency Fix_24_23",
                offset       =  0x0800 + i*4,
                bitSize      =  24,
                bitOffset    =  0,
                base         = pr.Int,
                mode         = "RW",
            ))

            self.add(pr.RemoteVariable(
                name         = f'amplitudeReadback[{i}]',
                hidden       = True,
                description  = "Loop filter output UFix_4_0",
                offset       =  0x1000 + i*4,
                bitSize      =  4,
                bitOffset    =  24,
                base         = pr.UInt,
                mode         = "RO",
            ))

            # Cryo channel readback loop filter output
            self.add(pr.RemoteVariable(
                name         = f'loopFilterOutput[{i}]',
                hidden       = True,
                description  = "Loop filter output UFix_24_24",
                offset       =  0x1000 + i*4,
                bitSize      =  24,
                bitOffset    =  0,
                base         = pr.UInt,
                mode         = "RO",
            ))

            # Cryo channel readback frequency error
            self.add(pr.RemoteVariable(
                name         = f'frequencyError[{i}]',
                hidden       = True,
                description  = "Frequency error MHz",
                offset       =  0x1800 + i*4,
                bitSize      =  24,
                bitOffset    =  0,
                base         = pr.Int,
                mode         = "RO",
            ))

            self.add(CryoChannel(
                name   = f'CryoChannel[{i}]',
                offset = (i*0x4),
                hidden = False,
                expand = False,
                index  = i,
                parent = self,
            ))

        # make waveform of etaMag 
        self.add(pr.LinkVariable(
            name         = "etaMagArray",
            hidden       = True,
            description  = "eta mag array (scaled)",
            dependencies = [self.node(f'etaMag[{i}]') for i in range(512)],
            linkedGet    = lambda dev, var, read: [val*2**-10 for val in dev.getArray(dev, var, read)],
            linkedSet    = lambda dev, var, value: dev.setArray( dev, var, [round(val*2**10) for val in value]),
            typeStr      = "List[Float64]",
        ))

        # make waveform of etaPhase 
        self.add(pr.LinkVariable(
            name         = "etaPhaseArray",
            hidden       = True,
            description  = "eta phase array (degree)",
            dependencies = [self.node(f'etaPhase[{i}]') for i in range(512)],
            linkedGet    = lambda dev, var, read: [val*180*2**-15 for val in dev.getArray(dev, var, read)],
            linkedSet    = lambda dev, var, value: dev.setArray( dev, var, [round(val*2**15./180) for val in value]),
            typeStr      = "List[Float64]",
        ))

        # make waveform of feedbackEnable
        self.add(pr.LinkVariable(
            name         = "feedbackEnableArray",
            hidden       = True,
            description  = "feedback enable array",
            dependencies = [self.node(f'feedbackEnable[{i}]') for i in range(512)],
            linkedGet    = self.getArray,
            linkedSet    = self.setArray,
            typeStr      = "List[UInt1]",
        ))

        # make waveform of amplitudeScale 
        self.add(pr.LinkVariable(
            name         = "amplitudeScaleArray",
            hidden       = True,
            description  = "amplitude scale array (0...15)",
            dependencies = [self.node(f'amplitudeScale[{i}]') for i in range(512)],
            linkedGet    = self.getArray,
            linkedSet    = self.setArray,
            typeStr      = "List[UInt4]",
        ))

        # make waveform of centerFrequencyMHz 
        self.add(pr.LinkVariable(
            name         = "centerFrequencyArray",
            hidden       = True,
            description  = "center frequency array (MHz)",
            dependencies = [self.node(f'centerFrequency[{i}]') for i in range(512)],
            linkedGet    = lambda dev, var, read: [val*2**-24*9.6 for val in dev.getArray(dev, var, read)],
            linkedSet    = lambda dev, var, value: dev.setArray( dev, var, [round(val*2**24./9.6) for val in value]),
            typeStr      = "List[Float64]",
        ))

        # make waveform of frequencyError
        self.add(pr.LinkVariable(
            name         = "frequencyErrorArray",
            hidden       = True,
            description  = "frequency error array (MHz)",
            dependencies = [self.node(f'frequencyError[{i}]') for i in range(512)],
            linkedGet    = lambda dev, var, read: [val*2**-23*9.6 for val in dev.getArray(dev, var, read)],
            typeStr      = "List[Float64]",
        ))

        self.add(pr.LocalVariable(
            name        = "etaScanChannel",
            description = "etaScan frequency band",
            mode        = "RW",
            value       = 0,
        ))

        # keeps track of whether or not an etaScan is currently
        # in progress.  default zero, meaning scan isn't running
        # currently.  runEtaScan sets it to one while it's scanning
        self.add(pr.LocalVariable(
            name        = "etaScanInProgress",
            description = "etaScan in progress",
            mode        = "RW",
            value       = 0,
        ))

        # make waveform for etaScanFreqs, 1000 will be our max number
        # make sure to initialize with type we want in EPICS (float)
        self.add(pr.LocalVariable(
            name        = "etaScanFreqs",
            hidden      = True,
            description = "etaScan frequencies",
            mode        = "RW",
            value       = [0.0 for x in range(1000)],
        ))

        self.add(pr.LocalVariable(
            name        = "etaScanResultsImag",
            hidden      = True,
            description = "etaScan frequencies",
            mode        = "RW",
            value       = [0.0 for x in range(1000)],
        ))

        self.add(pr.LocalVariable(
            name        = "etaScanResultsReal",
            hidden      = True,
            description = "etaScan frequencies",
            mode        = "RW",
            value       = [0.0 for x in range(1000)],
        ))

        self.add(pr.LocalVariable(
            name        = "etaScanDelF",
            description = "etaScan frequencies",
            mode        = "RW",
            value       = 0.05,
        ))

        self.add(pr.LocalVariable(
            name        = "etaScanDwell",
            description = "etaScan frequencies",
            mode        = "RW",
            value       = 0.0,
        ))

        self.add(pr.LocalVariable(
            name        = "etaScanAmplitude",
            description = "number of points to average for etaScan",
            mode        = "RW",
            value       = 0,
        ))

        @self.command(description="Run etaScan",)
        def runEtaScan():
            self.etaScanInProgress.set( 1 )

            # defer update callbacks
            with self.root.updateGroup():
                subchan = self.etaScanChannel.get()
                ampl    = self.etaScanAmplitude.get()
                freqs   = self.etaScanFreqs.get()
                # workaround for rogue local variables
                # list objects get written as string, not list of float when set by GUI
                if isinstance(freqs, str):
                    freqs = eval(freqs)
    
                dwell   = self.etaScanDwell.get()
                self.CryoChannel[subchan].amplitudeScale.set( ampl )
                self.CryoChannel[subchan].etaMagScaled.set( 1 )
                self.CryoChannel[subchan].feedbackEnable.set( 0 )
    
                # run scan in phase
                self.CryoChannel[subchan].etaPhaseDegree.set( 0 )
                resultsReal = []
                f           = []
                for freqMHz in freqs:
                    # is there overhead of setting freqMHz if prevFreqMHz == freqMHz
                    # out list of freqs may do several measurements at a single freq
                    # dont' want to write the same value again
                    if f != freqMHz:
                        f = freqMHz
                        self.CryoChannel[subchan].centerFrequencyMHz.set( f )
                    freqError = self.CryoChannel[subchan].frequencyError.get()
                    resultsReal.append( freqError )
    
                # run scan in quadrature
                self.CryoChannel[subchan].etaPhaseDegree.set( -90 )
                resultsImag = []
                f           = []
                for freqMHz in freqs:
                    if f != freqMHz:
                        f = freqMHz
                        self.CryoChannel[subchan].centerFrequencyMHz.set( f )
                    freqError = self.CryoChannel[subchan].frequencyError.get()
                    resultsImag.append( freqError )
               
    
                self.etaScanResultsReal.set( resultsReal )
                self.etaScanResultsImag.set( resultsImag )
    
            self.etaScanInProgress.set( 0 )

        @self.command(description="Set all amplitudeScale values",value=0)
        def setAmplitudeScales(arg):
            for c in self.CryoChannel.values():
                c.amplitudeScale.setDisp(arg, write=False)

            # Commit blocks with bulk background writes
            self.writeBlocks()

            # Verify the blocks with background transactions
            self.verifyBlocks()

            # Check write and verify results
            self.checkBlocks()

    @staticmethod
    def setArray(dev, var, value):
       # workaround for rogue local variables
       # list objects get written as string, not list of float when set by GUI
       if isinstance(value, str):
           value = eval(value)
       for variable, setpoint in zip( var.dependencies, value ):
           variable.set( setpoint, write=False )
       dev.writeBlocks()
       dev.verifyBlocks()
       dev.checkBlocks()

    @staticmethod
    def getArray(dev, var, read):
       if read:
          dev.readBlocks(variable=var.dependencies)
          dev.checkBlocks(variable=var.dependencies)
       return [variable.value() for variable in var.dependencies]


class CryoFreqBand(pr.Device):
    def __init__(   self,
            name        = "SysgenCryoBase",
            bandCenter  = 4250.0,
            description = "Cryo SYSGEN Module",
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)

        ##############################
        # Freq band parameters
        ##############################

        self.add(pr.LocalVariable(
            name        = "digitizerFrequencyMHz",
            description = "ADC/DAC sampling rate MHz",
            mode        = "RO",
            value       = 614.4,
        ))

        self.add(pr.LocalVariable(
            name        = "channelFrequencyMHz",
            description = "channel processing rate MHz",
            mode        = "RO",
            value       = 2.4,
        ))

        self.add(pr.LocalVariable(
            name        = "bandCenterMHz",
            description = "bandCenter MHz",
            mode        = "RW",
            value       = bandCenter,
        ))

        self.add(pr.LocalVariable(
            name        = "numberChannels",
            description = "number of channels",
            mode        = "RO",
            value       = 512,
        ))

        self.add(pr.LocalVariable(
            name        = "numberSubBands",
            description = "number of DSP sub bands",
            mode        = "RO",
            value       = 128,
        ))

        self.add(pr.LocalVariable(
            name        = "subBandNo",
            description = "frequency to subband",
            mode        = "RO",
            value       = [8, 24, 9, 25, 10, 26, 11, 27, 12, 28, 13, 29, 14, 30, 15, 31, 0, 16, 1, 17, 2, 18, 3, 19, 4, 20, 5, 21, 6, 22, 7, 23],
        ))

        ##############################
        # Devices
        ##############################
        self.add(CryoChannels(
            name   = 'CryoChannels',
            offset = 0x00010000,
            expand = False,
        ))

        ##############################
        # Registers
        ##############################
        self.add(pr.RemoteVariable(
            name         = "VersionNumber",
            description  = "Version Number",
            offset       =  0x000,
            bitSize      =  32,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RO",
        ))

        self.add(pr.RemoteVariable(
            name         = "ScratchPad",
            description  = "Scratch Pad Register",
            offset       =  0xFFC,
            bitSize      =  32,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

## config0
        self.add(pr.RemoteVariable(
            name         = "waveformSelect",
            description  = "Select waveform table",
            offset       =  0x80,
            bitSize      =  1,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))
        self.add(pr.RemoteVariable(
            name         = "noiseSelect",
            description  = "Play uniformly distributed PRNG",
            offset       =  0x80,
            bitSize      =  1,
            bitOffset    =  1,
            base         = pr.UInt,
            mode         = "RW",
        ))
        self.add(pr.RemoteVariable(
            name         = "rfEnable",
            description  = "Enable RF output",
            offset       =  0x80,
            bitSize      =  1,
            bitOffset    =  2,
            base         = pr.UInt,
            mode         = "RW",
        ))
## config0  end

## config1
        self.add(pr.RemoteVariable(
            name         = "iqSwapOut",
            description  = "Swap IQ channels on output",
            offset       =  0x84,
            bitSize      =  1,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "iqSwapIn",
            description  = "Swap IQ channels on input",
            offset       =  0x84,
            bitSize      =  1,
            bitOffset    =  1,
            base         = pr.UInt,
            mode         = "RW",
        ))
## config1  end

## config2
        self.add(pr.RemoteVariable(
            name         = "refPhaseDelay",
            description  = "Nubmer of cycles to delay phase referenece",
            offset       =  0x88,
            bitSize      =  3,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "toneScale",
            description  = "Scale the sum of 16 tones before synthesizer",
            offset       =  0x88,
            bitSize      =  2,
            bitOffset    =  3,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "feedbackEnable",
            description  = "Global feedback enable",
            offset       =  0x88,
            bitSize      =  1,
            bitOffset    =  5,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "feedbackPolarity",
            description  = "Global feedback polarity",
            offset       =  0x88,
            bitSize      =  1,
            bitOffset    =  6,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "swapDfIQ",
            description  = "Swap DF IQ",
            offset       =  0x88,
            bitSize      =  1,
            bitOffset    =  7,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "statusChannelSelect",
            description  = "Select channel for status registers",
            offset       =  0x88,
            bitSize      =  9,
            bitOffset    =  8,
            base         = pr.UInt,
            mode         = "RW",
        ))
## config2  end

## config3
        self.add(pr.RemoteVariable(
            name         = "feedbackGain",
            description  = "Feedback gain UFix_16_12",
            offset       =  0x8C,
            bitSize      =  16,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))
        self.add(pr.RemoteVariable(
            name         = "feedbackLimit",
            description  = "Feedback limit UFix_16_16",
            offset       =  0x8C,
            bitSize      =  16,
            bitOffset    =  16,
            base         = pr.UInt,
            mode         = "RW",
        ))
## config3  end

## config4
        self.add(pr.RemoteVariable(
            name         = "filterAlpha",
            description  = "IIR filter alpha UFix16_15",
            offset       =  0x90,
            bitSize      =  16,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

## config4 end
        self.add(pr.RemoteVariable(
            name         = "loopFilterOutputSel",
            description  = "Global loop filter out reg.  Select with ",
            offset       =  0x94,
            bitSize      =  7,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "analysisScale",
            description  = "analysis filter bank scale, nominal value is 1",
            offset       =  0x98,
            bitSize      =  2,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "synthesisScale",
            description  = "synthesis filter bank scale, nominal value is 2",
            offset       =  0x98,
            bitSize      =  2,
            bitOffset    =  2,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "decimation",
            description  = "debug decimation rate 0...7",
            offset       =  0x98,
            bitSize      =  3,
            bitOffset    =  4,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "singleChannelReadout",
            description  = "select for single channel readout",
            offset       =  0x9C,
            bitSize      =  1,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "singleChannelReadoutOpt2",
            description  = "non-decimated single channel readout - rate 307.2e6/128",
            offset       =  0x9C,
            bitSize      =  1,
            bitOffset    =  10,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "iqStreamEnable",
            description  = "readout IQ data instead of freq/freqError",
            offset       =  0x9C,
            bitSize      =  1,
            bitOffset    =  11,
            base         = pr.UInt,
            mode         = "RW",
        ))


        self.add(pr.RemoteVariable(
            name         = "readoutChannelSelect",
            description  = "select for single channel readout",
            offset       =  0x9C,
            bitSize      =  9,
            bitOffset    =  1,
            base         = pr.UInt,
            mode         = "RW",
        ))



        self.add(pr.RemoteVariable(
            name         = "dspReset",
            description  = "reset DSP core",
            offset       =  0x100,
            bitSize      =  1,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "dspEnable",
            description  = "Enable DSP core",
            offset       =  0x100,
            bitSize      =  1,
            bitOffset    =  1,
            base         = pr.UInt,
            mode         = "RW",
        ))


        self.add(pr.RemoteVariable(
            name         = "refPhaseDelayFine",
            description  = "fine delay control (307.2MHz clock)",
            offset       =  0x100,
            bitSize      =  8,
            bitOffset    =  2,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "lmsDelay",
            description  = "Match system latency for LMS feedback (2.4MHz ticks)",
            offset       =  0x100,
            bitSize      =  3,
            bitOffset    =  13,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "lmsGain",
            description  = "LMS gain, powers of 2",
            offset       =  0x100,
            bitSize      =  3,
            bitOffset    =  10,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "lmsEnable1",
            description  = "Enable 1st harmonic tracking",
            offset       =  0x100,
            bitSize      =  1,
            bitOffset    =  16,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "lmsEnable2",
            description  = "Enable 2nd harmonic tracking",
            offset       =  0x100,
            bitSize      =  1,
            bitOffset    =  17,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "lmsEnable3",
            description  = "Enable 3rd harmonic tracking",
            offset       =  0x100,
            bitSize      =  1,
            bitOffset    =  18,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "lmsRstDly",
            description  = "disable feedback after reset (2.4MHz ticks)",
            offset       =  0x100,
            bitSize      =  6,
            bitOffset    =  26,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.RemoteVariable(
            name         = "lmsFreq",
            description  = "LMS frequency = flux ramp freq * nPhi0",
            offset       =  0x104,
            bitSize      =  24,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))

        self.add(pr.LinkVariable(
            name         = "lmsFreqHz",
            description  = "LMS frequency = flux ramp freq * nPhi0",
            dependencies = [self.lmsFreq],
            linkedGet    = lambda: self.lmsFreq.value()*(2**-24)*(2.4*10**6),
            linkedSet    = lambda value, write: self.lmsFreq.set(round(value*(2**24)/(2.4*10**6)), write=write),
            typeStr      = "Float64",
        ))
        self.add(pr.RemoteVariable(
            name         = "lmsDlyFine",
            description  = "fine delay control (38.4MHz ticks)",
            offset       =  0x100,
            bitSize      =  4,
            bitOffset    =  22,
            base         = pr.UInt,
            mode         = "RW",
        ))
        self.add(pr.RemoteVariable(
            name         = "lmsDelay2",
            description  = "delay DDS counter reset (307.2MHz ticks)",
            offset       =  0x104,
            bitSize      =  8,
            bitOffset    =  24,
            base         = pr.UInt,
            mode         = "RW",
        ))
        self.add(pr.RemoteVariable(
            name         = "streamEnable",
            description  = "Enable streaming",
            offset       =  0x108,
            bitSize      =  1,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
        ))










## status1
        self.add(pr.RemoteVariable(
            name         = "Q",
            description  = "Q readback Fix_16_15",
            offset       =  0x08,
            bitSize      =  16,
            bitOffset    =  0,
            base         = pr.Int,
            mode         = "RO",
##            pollInterval = 1,
        ))
        self.add(pr.RemoteVariable(
            name         = "I",
            description  = "I readback Fix_16_15",
            offset       =  0x08,
            bitSize      =  16,
            bitOffset    =  16,
            base         = pr.Int,
            mode         = "RO",
##            pollInterval = 1,
        ))
## status1 end

## status 2
        self.add(pr.RemoteVariable(
            name         = "dspCounter",
            description  = "32 bit counter, dsp clock domain UFix_32_0",
            offset       =  0x0C,
            bitSize      =  32,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RO",
        ))
## status2 end
        self.add(pr.RemoteVariable(
            name         = "loopFilterOutput",
            description  = "Loop filter output UFix_32_0",
            offset       =  0x10,
            bitSize      =  32,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RO",
        ))


#        for i in range(512):
#            if (i % 16 == 0) :
#                self.CryoChannels.CryoChannel[i].centerFrequency.addListener(self.UpdateIQ)

        # ##############################
        # # Commands
        # ##############################
        # @self.command(description="Starts the signal generator pattern",)
        # def CmdClearErrors():
            # self.StartSigGenReg.set(1)
            # self.StartSigGenReg.set(0)

    def UpdateIQ(self, dev, value, disp):
##        time.sleep(0.001)
        self.I.get()
        self.Q.get()

class CryoAdcMux(pr.Device):
    def __init__(   self,
            name        = "CryoAdcMux",
            description = "",
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)

        self.addRemoteVariables(
            name         = "Remap",
            description  = "",
            offset       =  0x0,
            bitSize      =  1,
            bitOffset    =  0,
            base         = pr.UInt,
            mode         = "RW",
            number       =  2,
            stride       =  1,
        )

class SysgenCryo(pr.Device):
    def __init__(   self,
            name        = "SysgenCryo",
            numberPairs = 1,
            description = "Cryo SYSGEN Module",
            **kwargs):
        super().__init__(name=name, description=description, **kwargs)

        bandCenters = [4750.0, 4250.0, 5750.0, 5250.0]

        ##############################
        # Devices
        ##############################
        for i in range(2, 4):
            self.add(CryoFreqBand(
                name       = ('Base[%d]'%i),
                bandCenter = bandCenters[i],
                offset     = (i*0x00100000),
                expand     = False,
            ))


        self.add(CryoAdcMux(
            name   = 'CryoAdcMux',
            offset = 0x00800000,
            expand = False,
        ))
