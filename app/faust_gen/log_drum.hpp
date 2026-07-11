/* ------------------------------------------------------------
name: "log_drum"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn LogDrum -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __LogDrum_H__
#define  __LogDrum_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS LogDrum
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

class LogDrumSIG0 {
	
  private:
	
	int iVec2[2];
	int iRec3[2];
	
  public:
	
	int getNumInputsLogDrumSIG0() {
		return 0;
	}
	int getNumOutputsLogDrumSIG0() {
		return 1;
	}
	
	void instanceInitLogDrumSIG0(int sample_rate) {
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iVec2[l3] = 0;
		}
		for (int l4 = 0; l4 < 2; l4 = l4 + 1) {
			iRec3[l4] = 0;
		}
	}
	
	void fillLogDrumSIG0(int count, float* table) {
		for (int i1 = 0; i1 < count; i1 = i1 + 1) {
			iVec2[0] = 1;
			iRec3[0] = (iVec2[1] + iRec3[1]) % 65536;
			table[i1] = std::sin(9.58738e-05f * float(iRec3[0]));
			iVec2[1] = iVec2[0];
			iRec3[1] = iRec3[0];
		}
	}

};

static LogDrumSIG0* newLogDrumSIG0() { return (LogDrumSIG0*)new LogDrumSIG0(); }
static void deleteLogDrumSIG0(LogDrumSIG0* dsp) { delete dsp; }

static float LogDrum_faustpower2_f(float value) {
	return value * value;
}
static float ftbl0LogDrumSIG0[65536];

class LogDrum : public dsp {
	
 private:
	
	int iVec0[2];
	int fSampleRate;
	float fConst0;
	float fConst2;
	float fConst4;
	float fConst6;
	float fConst8;
	float fConst10;
	float fConst11;
	FAUSTFLOAT fButton0;
	float fVec1[2];
	int iRec2[2];
	float fConst12;
	float fConst13;
	float fConst14;
	float fConst15;
	FAUSTFLOAT fHslider0;
	float fConst16;
	float fRec4[2];
	float fRec1[3];
	FAUSTFLOAT fHslider1;
	int iRec5[2];
	float fConst17;
	float fRec6[2];
	float fConst18;
	float fConst19;
	FAUSTFLOAT fHslider2;
	float fConst20;
	float fRec7[2];
	FAUSTFLOAT fHslider3;
	float fRec0[3];
	float fConst21;
	
 public:
	LogDrum() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn LogDrum -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/adsr:author", "Yann Orlarey and Andrey Bundin");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "log_drum.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:author", "Julius O. Smith III");
		m->declare("filters.lib/lowpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/lowpass:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonlp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonlp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonlp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "log_drum");
		m->declare("oscillators.lib/name", "Faust Oscillator Library");
		m->declare("oscillators.lib/version", "1.5.0");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
		LogDrumSIG0* sig0 = newLogDrumSIG0();
		sig0->instanceInitLogDrumSIG0(sample_rate);
		sig0->fillLogDrumSIG0(65536, ftbl0LogDrumSIG0);
		deleteLogDrumSIG0(sig0);
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(7539.8223f / fConst0);
		fConst2 = 2.0f * (1.0f - 1.0f / LogDrum_faustpower2_f(fConst1));
		float fConst3 = 1.0f / fConst1;
		fConst4 = (fConst3 + -1.4142135f) / fConst1 + 1.0f;
		float fConst5 = (fConst3 + 1.4142135f) / fConst1 + 1.0f;
		fConst6 = 1.0f / fConst5;
		float fConst7 = std::tan(4084.0706f / fConst0);
		fConst8 = 2.0f * (1.0f - 1.0f / LogDrum_faustpower2_f(fConst7));
		float fConst9 = 1.0f / fConst7;
		fConst10 = (fConst9 + -0.45454547f) / fConst7 + 1.0f;
		fConst11 = 1.0f / ((fConst9 + 0.45454547f) / fConst7 + 1.0f);
		fConst12 = std::max<float>(1.0f, 0.001f * fConst0);
		fConst13 = 1.0f / fConst12;
		fConst14 = 1.0f / std::max<float>(1.0f, 0.09f * fConst0);
		fConst15 = 1.0f / std::max<float>(1.0f, 0.028f * fConst0);
		fConst16 = 2.0f / fConst0;
		fConst17 = 1.0f / std::max<float>(1.0f, 0.07f * fConst0);
		fConst18 = std::max<float>(1.0f, 0.004f * fConst0);
		fConst19 = 1.0f / fConst18;
		fConst20 = 1.0f / fConst0;
		fConst21 = 0.444f / fConst5;
	}
	
	virtual void instanceResetUserInterface() {
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider0 = FAUSTFLOAT(98.0f);
		fHslider1 = FAUSTFLOAT(0.65f);
		fHslider2 = FAUSTFLOAT(0.32f);
		fHslider3 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			iVec0[l0] = 0;
		}
		for (int l1 = 0; l1 < 2; l1 = l1 + 1) {
			fVec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 2; l2 = l2 + 1) {
			iRec2[l2] = 0;
		}
		for (int l5 = 0; l5 < 2; l5 = l5 + 1) {
			fRec4[l5] = 0.0f;
		}
		for (int l6 = 0; l6 < 3; l6 = l6 + 1) {
			fRec1[l6] = 0.0f;
		}
		for (int l7 = 0; l7 < 2; l7 = l7 + 1) {
			iRec5[l7] = 0;
		}
		for (int l8 = 0; l8 < 2; l8 = l8 + 1) {
			fRec6[l8] = 0.0f;
		}
		for (int l9 = 0; l9 < 2; l9 = l9 + 1) {
			fRec7[l9] = 0.0f;
		}
		for (int l10 = 0; l10 < 3; l10 = l10 + 1) {
			fRec0[l10] = 0.0f;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual LogDrum* clone() {
		return new LogDrum();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("log_drum");
		ui_interface->addHorizontalSlider("decay", &fHslider2, FAUSTFLOAT(0.32f), FAUSTFLOAT(0.08f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(98.0f), FAUSTFLOAT(2e+01f), FAUSTFLOAT(2e+03f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("gain", &fHslider3, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->addHorizontalSlider("knock", &fHslider1, FAUSTFLOAT(0.65f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.2f), FAUSTFLOAT(0.01f));
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = float(fButton0);
		float fSlow1 = float(fHslider0);
		float fSlow2 = fConst16 * fSlow1;
		float fSlow3 = fConst11 * float(fHslider1);
		int iSlow4 = fSlow0 == 0.0f;
		float fSlow5 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider2));
		float fSlow6 = fConst20 * fSlow1;
		float fSlow7 = float(fHslider3);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			iVec0[0] = 1;
			fVec1[0] = fSlow0;
			iRec2[0] = (fSlow0 > fVec1[1]) + (fSlow0 <= fVec1[1]) * (iRec2[1] + (iRec2[1] > 0));
			float fTemp0 = float(iRec2[0]);
			float fTemp1 = fConst13 * fTemp0;
			float fTemp2 = fConst12 - fTemp0;
			int iTemp3 = 1 - iVec0[1];
			float fTemp4 = ((iTemp3) ? 0.0f : fRec4[1] + fSlow2 * (0.9f * std::max<float>(0.0f, std::min<float>(fTemp1, fConst15 * fTemp2 + 1.0f)) + 1.0f));
			fRec4[0] = fTemp4 - std::floor(fTemp4);
			fRec1[0] = ftbl0LogDrumSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec4[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fTemp1, fConst14 * fTemp2 + 1.0f)) - fConst11 * (fConst10 * fRec1[2] + fConst8 * fRec1[1]);
			iRec5[0] = iSlow4 * (iRec5[1] + 1);
			fRec6[0] = fSlow0 + fRec6[1] * float(fVec1[1] >= fSlow0);
			float fTemp5 = ((iTemp3) ? 0.0f : fSlow6 + fRec7[1]);
			fRec7[0] = fTemp5 - std::floor(fTemp5);
			fRec0[0] = fSlow7 * (ftbl0LogDrumSIG0[std::max<int>(0, std::min<int>(int(65536.0f * fRec7[0]), 65535))] * std::max<float>(0.0f, std::min<float>(fConst19 * fRec6[0], std::max<float>(fSlow5 * (fConst18 - fRec6[0]) + 1.0f, 0.0f)) * (1.0f - fConst17 * float(iRec5[0]))) + fSlow3 * (fRec1[2] + fRec1[0] + 2.0f * fRec1[1])) - fConst6 * (fConst4 * fRec0[2] + fConst2 * fRec0[1]);
			float fTemp6 = fConst21 * (fRec0[2] + fRec0[0] + 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp6);
			output1[i0] = FAUSTFLOAT(fTemp6);
			iVec0[1] = iVec0[0];
			fVec1[1] = fVec1[0];
			iRec2[1] = iRec2[0];
			fRec4[1] = fRec4[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			iRec5[1] = iRec5[0];
			fRec6[1] = fRec6[0];
			fRec7[1] = fRec7[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
		}
	}

};

#endif
